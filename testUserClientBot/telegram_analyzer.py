import asyncio
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse

from pyrogram import Client
from pyrogram.types import Chat, Message, User
from pyrogram.errors import (
    ChannelPrivate, ChatAdminRequired, FloodWait, 
    UsernameNotOccupied, PeerIdInvalid
)
from pymongo import MongoClient
from bson import ObjectId
import logging
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()
# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramAnalyzer:
    def __init__(self, api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.app = Client("telegram_analyzer", api_id=api_id, api_hash=api_hash)
        
        # ایجاد فولدرها
        os.makedirs("results", exist_ok=True)
        os.makedirs("users", exist_ok=True)
        
        # مجموعه‌های نگهداری داده
        self.processed_users: Dict[int, Dict] = {}
        self.extracted_links: Set[str] = set()

    def extract_links_from_text(self, text: str) -> List[str]:
        """استخراج لینک‌ها از متن"""
        if not text:
            return []
            
        # الگوهای مختلف لینک
        patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r't\.me/[^\s]+',
            r'@\w+',
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            links.extend(matches)
        
        return links

    async def analyze_chat_type(self, chat_link: str) -> Dict:
        """تحلیل نوع چت (گروه/کانال عمومی/خصوصی)"""
        result = {
            "link": chat_link,
            "type": "unknown",
            "status": "unknown",
            "title": "",
            "username": "",
            "members_count": 0,
            "error": None
        }
        
        try:
            # استخراج username از لینک
            username = chat_link.replace("https://t.me/", "").replace("@", "").split("?")[0]
            
            chat = await self.app.get_chat(username)
            
            result["title"] = chat.title or ""
            result["username"] = chat.username or ""
            result["members_count"] = getattr(chat, 'members_count', 0)
            
            if chat.type.name == "CHANNEL":
                result["type"] = "channel"
            elif chat.type.name in ["GROUP", "SUPERGROUP"]:
                result["type"] = "group"
            
            result["status"] = "public"
            
        except ChannelPrivate:
            result["status"] = "private"
            result["error"] = "Channel/Group is private"
        except (UsernameNotOccupied, PeerIdInvalid):
            result["error"] = "Invalid username or link"
        except Exception as e:
            result["error"] = str(e)
            
        return result

    async def process_user_message(self, message: Message, group_id: str):
        """پردازش پیام کاربر و ذخیره اطلاعات"""
        if not message.from_user:
            return
            
        user = message.from_user
        user_id = user.id
        
        # اگر کاربر جدید است، ایجاد رکورد اولیه
        if user_id not in self.processed_users:
            self.processed_users[user_id] = {
                "user_id": user_id,
                "current_username": user.username,
                "current_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "username_history": [],
                "name_history": [],
                "is_bot": user.is_bot,
                "is_deleted": user.is_deleted,
                "joined_groups": [],
                "messages": []
            }
        
        user_data = self.processed_users[user_id]
        
        # بروزرسانی username اگر تغییر کرده
        if user.username and user.username != user_data["current_username"]:
            if user_data["current_username"]:
                user_data["username_history"].append({
                    "username": user_data["current_username"],
                    "changed_at": datetime.utcnow().isoformat()
                })
            user_data["current_username"] = user.username
        
        # بروزرسانی نام اگر تغییر کرده
        current_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if current_name and current_name != user_data["current_name"]:
            if user_data["current_name"]:
                user_data["name_history"].append({
                    "name": user_data["current_name"],
                    "changed_at": datetime.utcnow().isoformat()
                })
            user_data["current_name"] = current_name
        
        # اضافه کردن گروه به لیست گروه‌های عضو شده (اگر وجود نداشته باشد)
        group_exists = any(g["group_id"] == group_id for g in user_data["joined_groups"])
        if not group_exists:
            user_data["joined_groups"].append({
                "group_id": group_id,
                "joined_at": datetime.utcnow().isoformat(),
                "role": "member",
                "is_admin": False
            })
        
        # اضافه کردن پیام
        reactions = []
        if hasattr(message, 'reactions') and message.reactions:
            reactions = [reaction.emoji for reaction in message.reactions.reactions]
        
        message_data = {
            "group_id": group_id,
            "message_id": message.id,
            "text": message.text or message.caption or "",
            "timestamp": message.date.isoformat() if message.date else None,
            "reactions": reactions,
            "reply_to": message.reply_to_message_id,
            "edited": bool(message.edit_date),
            "is_forwarded": bool(message.forward_date)
        }
        
        user_data["messages"].append(message_data)

    async def analyze_chat_messages(self, chat_link: str, chat_info: Dict):
        """تحلیل پیام‌های چت و استخراج لینک‌ها"""
        if chat_info["status"] != "public":
            logger.warning(f"Skipping private chat: {chat_link}")
            return
        
        try:
            username = chat_link.replace("https://t.me/", "").replace("@", "").split("?")[0]
            chat = await self.app.get_chat(username)
            
            logger.info(f"Analyzing messages in: {chat.title}")
            
            message_count = 0
            async for message in self.app.get_chat_history(chat.id):
                message_count += 1
                
                # پردازش کاربر پیام
                await self.process_user_message(message, str(chat.id))
                
                # استخراج لینک‌ها از متن پیام
                text = message.text or message.caption or ""
                links = self.extract_links_from_text(text)
                
                for link in links:
                    self.extracted_links.add(link)
                
                # محدودیت برای تست
                if message_count % 100 == 0:
                    logger.info(f"Processed {message_count} messages...")
                    
                # جلوگیری از flood
                await asyncio.sleep(0.1)
                
        except FloodWait as e:
            logger.warning(f"FloodWait: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"Error analyzing chat {chat_link}: {e}")

    def save_results_to_files(self):
        """ذخیره نتایج در فایل‌ها"""
        logger.info("Saving results to files...")
        
        # ذخیره لینک‌های استخراج شده
        with open("results/extracted_links.txt", "w", encoding="utf-8") as f:
            for link in sorted(self.extracted_links):
                f.write(f"{link}")
        
        logger.info(f"Extracted {len(self.extracted_links)} links saved to results/extracted_links.txt")
        
        # ذخیره اطلاعات کاربران در فایل‌های JSON
        for user_id, user_data in self.processed_users.items():
            user_filename = f"users/user_{user_id}.json"
            
            with open(user_filename, "w", encoding="utf-8") as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.processed_users)} user files to users/ directory")
        
        # ذخیره خلاصه کلی
        summary = {
            "total_users": len(self.processed_users),
            "total_extracted_links": len(self.extracted_links),
            "analysis_date": datetime.utcnow().isoformat(),
            "user_statistics": {}
        }
        
        # آمار کاربران
        for user_id, user_data in self.processed_users.items():
            summary["user_statistics"][str(user_id)] = {
                "username": user_data["current_username"],
                "name": user_data["current_name"],
                "total_messages": len(user_data["messages"]),
                "joined_groups_count": len(user_data["joined_groups"]),
                "is_bot": user_data["is_bot"]
            }
        
        with open("results/analysis_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info("Analysis summary saved to results/analysis_summary.json")

    async def run_analysis(self, chat_links: List[str]):
        """اجرای تحلیل کامل"""
        async with self.app:
            logger.info("Starting Telegram analysis...")
            
            # تحلیل نوع چت‌ها
            chat_results = []
            for i, link in enumerate(chat_links, 1):
                logger.info(f"[{i}/{len(chat_links)}] Analyzing chat type: {link}")
                result = await self.analyze_chat_type(link)
                chat_results.append(result)
                
                # ذخیره نتیجه فوری
                with open("results/chat_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(chat_results, f, ensure_ascii=False, indent=2)
                
                await asyncio.sleep(1)  # جلوگیری از flood
            
            logger.info(f"Chat analysis completed. Found {len([r for r in chat_results if r['status'] == 'public'])} public chats")
            
            # تحلیل پیام‌ها برای چت‌های عمومی
            public_chats = [r for r in chat_results if r["status"] == "public"]
            for i, result in enumerate(public_chats, 1):
                logger.info(f"[{i}/{len(public_chats)}] Analyzing messages for: {result.get('title', result['link'])}")
                await self.analyze_chat_messages(result["link"], result)
            
            # ذخیره نتایج نهایی
            self.save_results_to_files()
            
            logger.info("Analysis completed successfully!")

def main():
    print("🚀 Telegram Channel/Group Analyzer")
    print("=" * 50)
    
    # تنظیمات API تلگرام
    API_ID = input("Enter your API ID: ").strip()
    API_HASH = input("Enter your API HASH: ").strip()
    
    if not API_ID or not API_HASH:
        print("❌ API ID and API HASH are required!")
        return
    
    try:
        API_ID = int(API_ID)
    except ValueError:
        print("❌ API ID must be a number!")
        return
    
    # لیست لینک‌ها
    links_file = "links.txt"
    
    if os.path.exists(links_file):
        with open(links_file, "r", encoding="utf-8") as f:
            chat_links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        # ایجاد فایل نمونه
        sample_links = [
            "# Add your Telegram links here (one per line)",
            "# Examples:",
            "# https://t.me/python",
            "# https://t.me/telegram",
            "# @channel_username",
            "",
            "https://t.me/python"
        ]
        
        with open(links_file, "w", encoding="utf-8") as f:
            for link in sample_links:
                f.write(f"{link}")
        
        print(f"📁 Sample file '{links_file}' created.")
        print("Please add your Telegram links to this file and run the program again.")
        return
    
    if not chat_links:
        print("❌ No links found in links.txt!")
        return
    
    print(f"📋 Found {len(chat_links)} links to analyze")
    
    # تایید از کاربر
    response = input("Do you want to continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    # اجرای تحلیل
    analyzer = TelegramAnalyzer(API_ID, API_HASH)
    try:
        asyncio.run(analyzer.run_analysis(chat_links))
        
        print("✅ Analysis completed successfully!")
        print(f"📁 Results saved in:")
        print(f"   - results/chat_analysis.json (Chat types)")
        print(f"   - results/extracted_links.txt (All extracted links)")
        print(f"   - results/analysis_summary.json (Summary)")
        print(f"   - users/ directory (Individual user files)")
        
    except KeyboardInterrupt:
        print("⏹️ Analysis stopped by user")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()