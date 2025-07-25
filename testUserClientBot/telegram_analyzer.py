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
from dotenv import load_dotenv
import logging

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramAnalyzer:
    def __init__(self):
        # خواندن تنظیمات از فایل .env
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.output_file = os.getenv('OUTPUT_FILE', 'my_chats.json')
        self.session_string = os.getenv('SESSION_STRING')
        
        # اگر SESSION_STRING موجود باشد از آن استفاده کن، وگرنه session جدید بساز
        if self.session_string:
            self.app = Client(
                "telegram_analyzer",
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_string=self.session_string
            )
        else:
            self.app = Client(
                "telegram_analyzer",
                api_id=self.api_id,
                api_hash=self.api_hash
            )
        
        # ایجاد فولدرها
        os.makedirs("results", exist_ok=True)
        os.makedirs("users", exist_ok=True)
        
        # مجموعه‌های نگهداری داده
        self.processed_users: Dict[int, Dict] = {}
        self.extracted_links: Set[str] = set()
        self.chat_analysis_results: List[Dict] = []

    def extract_links_from_text(self, text: str) -> List[str]:
        """استخراج لینک‌ها از متن"""
        if not text:
            return []
            
        # الگوهای مختلف لینک
        patterns = [
            r'https?://[^\s<>"\']+',
            r'www\.[^\s<>"\']+',
            r't\.me/[^\s<>"\']+',
            r'@[a-zA-Z0-9_]+',
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            links.extend(matches)
        
        # پاکسازی لینک‌ها
        cleaned_links = []
        for link in links:
            # حذف کاراکترهای اضافی از انتها
            link = re.sub(r'[.,;:!?)\]}]+$', '', link)
            if link:
                cleaned_links.append(link)
        
        return cleaned_links

    async def analyze_chat_type(self, chat_link: str) -> Dict:
        """تحلیل نوع چت (گروه/کانال عمومی/خصوصی)"""
        result = {
            "link": chat_link,
            "type": "unknown",
            "status": "unknown",
            "title": "",
            "username": "",
            "members_count": 0,
            "chat_id": None,
            "error": None
        }
        
        try:
            # استخراج username از لینک
            username = chat_link.replace("https://t.me/", "").replace("@", "").split("?")[0].split("/")[0]
            
            chat = await self.app.get_chat(username)
            
            result["title"] = chat.title or ""
            result["username"] = chat.username or ""
            result["members_count"] = getattr(chat, 'members_count', 0)
            result["chat_id"] = chat.id
            
            if chat.type.name == "CHANNEL":
                result["type"] = "channel"
            elif chat.type.name in ["GROUP", "SUPERGROUP"]:
                result["type"] = "group"
            elif chat.type.name == "PRIVATE":
                result["type"] = "private"
            
            result["status"] = "public"
            
        except ChannelPrivate:
            result["status"] = "private"
            result["error"] = "Channel/Group is private"
        except (UsernameNotOccupied, PeerIdInvalid):
            result["error"] = "Invalid username or link"
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error analyzing {chat_link}: {e}")
            
        return result

    async def process_user_message(self, message: Message, group_id: str, group_title: str = ""):
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
                "is_bot": user.is_bot or False,
                "is_deleted": user.is_deleted or False,
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
                "group_title": group_title,
                "joined_at": datetime.utcnow().isoformat(),
                "role": "member",
                "is_admin": False
            })
        
        # اضافه کردن پیام
        reactions = []
        if hasattr(message, 'reactions') and message.reactions:
            for reaction in message.reactions.reactions:
                reactions.append(reaction.emoji)
        
        message_data = {
            "group_id": group_id,
            "message_id": message.id,
            "text": message.text or message.caption or "",
            "timestamp": message.date.isoformat() if message.date else datetime.utcnow().isoformat(),
            "reactions": reactions,
            "reply_to": message.reply_to_message_id,
            "edited": bool(message.edit_date),
            "is_forwarded": bool(message.forward_date)
        }
        
        user_data["messages"].append(message_data)

    async def analyze_chat_messages(self, chat_link: str, chat_info: Dict, limit: int = 1000):
        """تحلیل پیام‌های چت و استخراج لینک‌ها"""
        if chat_info["status"] != "public" or chat_info.get("error"):
            logger.warning(f"Skipping chat: {chat_link} - {chat_info.get('error', 'Private/Invalid')}")
            return
        
        try:
            chat_id = chat_info["chat_id"]
            chat_title = chat_info["title"]
            
            logger.info(f"📥 Analyzing messages in: {chat_title} (limit: {limit})")
            
            message_count = 0
            async for message in self.app.get_chat_history(chat_id, limit=limit):
                message_count += 1
                
                # پردازش کاربر پیام
                await self.process_user_message(message, str(chat_id), chat_title)
                
                # استخراج لینک‌ها از متن پیام
                text = message.text or message.caption or ""
                links = self.extract_links_from_text(text)
                
                for link in links:
                    self.extracted_links.add(link)
                
                # لاگ پیشرفت
                if message_count % 100 == 0:
                    logger.info(f"   📊 Processed {message_count} messages...")
                    
                # جلوگیری از flood
                await asyncio.sleep(0.05)
                
            logger.info(f"✅ Completed: {message_count} messages from {chat_title}")
                
        except FloodWait as e:
            logger.warning(f"⏳ FloodWait: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"❌ Error analyzing chat {chat_link}: {e}")

    def save_results_to_files(self):
        """ذخیره نتایج در فایل‌ها"""
        logger.info("💾 Saving results to files...")
        
        # 1. ذخیره تحلیل چت‌ها
        with open("results/chat_analysis.json", "w", encoding="utf-8") as f:
            json.dump(self.chat_analysis_results, f, ensure_ascii=False, indent=2)
        
        # 2. ذخیره لینک‌های استخراج شده
        with open("results/extracted_links.txt", "w", encoding="utf-8") as f:
            for link in sorted(self.extracted_links):
                f.write(f"{link}\n")
        
        # 3. ذخیره تمام لینک‌ها در فایل JSON هم
        with open("results/extracted_links.json", "w", encoding="utf-8") as f:
            json.dump(list(sorted(self.extracted_links)), f, ensure_ascii=False, indent=2)
        
        # 4. ذخیره اطلاعات کاربران در فایل‌های JSON جداگانه
        for user_id, user_data in self.processed_users.items():
            user_filename = f"users/user_{user_id}.json"
            
            with open(user_filename, "w", encoding="utf-8") as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        # 5. ذخیره خلاصه کلی
        summary = {
            "analysis_info": {
                "total_chats_analyzed": len(self.chat_analysis_results),
                "public_chats": len([c for c in self.chat_analysis_results if c["status"] == "public"]),
                "private_chats": len([c for c in self.chat_analysis_results if c["status"] == "private"]),
                "total_users": len(self.processed_users),
                "total_extracted_links": len(self.extracted_links),
                "analysis_date": datetime.utcnow().isoformat()
            },
            "chat_types": {
                "channels": len([c for c in self.chat_analysis_results if c["type"] == "channel"]),
                "groups": len([c for c in self.chat_analysis_results if c["type"] == "group"]),
                "unknown": len([c for c in self.chat_analysis_results if c["type"] == "unknown"])
            },
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
        
        # 6. ذخیره خلاصه در فایل تعیین شده در .env
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        with open("results/analysis_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 7. آمار نهایی
        logger.info("📊 Analysis Results:")
        logger.info(f"   • Total chats: {len(self.chat_analysis_results)}")
        logger.info(f"   • Public chats: {summary['analysis_info']['public_chats']}")
        logger.info(f"   • Private chats: {summary['analysis_info']['private_chats']}")
        logger.info(f"   • Total users: {len(self.processed_users)}")
        logger.info(f"   • Extracted links: {len(self.extracted_links)}")
        logger.info(f"   • User files created: {len(self.processed_users)}")

    async def run_analysis(self, chat_links: List[str], messages_per_chat: int = 1000):
        """اجرای تحلیل کامل"""
        async with self.app:
            logger.info("🚀 Starting Telegram analysis...")
            logger.info(f"📋 Total links to analyze: {len(chat_links)}")
            
            # مرحله 1: تحلیل نوع چت‌ها
            logger.info("🔍 Phase 1: Analyzing chat types...")
            for i, link in enumerate(chat_links, 1):
                logger.info(f"   [{i}/{len(chat_links)}] {link}")
                result = await self.analyze_chat_type(link)
                self.chat_analysis_results.append(result)
                
                # ذخیره فوری نتایج
                with open("results/chat_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(self.chat_analysis_results, f, ensure_ascii=False, indent=2)
                
                await asyncio.sleep(1)  # جلوگیری از flood
            
            # مرحله 2: تحلیل پیام‌ها
            public_chats = [r for r in self.chat_analysis_results if r["status"] == "public"]
            logger.info(f"📥 Phase 2: Analyzing messages from {len(public_chats)} public chats...")
            
            for i, chat_info in enumerate(public_chats, 1):
                logger.info(f"   [{i}/{len(public_chats)}] Processing: {chat_info.get('title', chat_info['link'])}")
                await self.analyze_chat_messages(chat_info["link"], chat_info, messages_per_chat)
                
                # ذخیره میانی
                if i % 5 == 0:  # هر 5 چت یکبار ذخیره کن
                    logger.info("💾 Saving intermediate results...")
                    self.save_results_to_files()
            
            # مرحله 3: ذخیره نتایج نهایی
            logger.info("💾 Phase 3: Saving final results...")
            self.save_results_to_files()
            
            logger.info("✅ Analysis completed successfully!")

def main():
    print("🎯 Telegram Channel/Group Analyzer v2.0")
    print("=" * 50)
    
    # بررسی وجود فایل .env
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your configuration.")
        return
    
    # بررسی متغیرهای محیطی ضروری
    required_vars = ['API_ID', 'API_HASH']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    # خواندن لینک‌ها
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
            "https://t.me/python",
            "https://t.me/telegram"
        ]
        
        with open(links_file, "w", encoding="utf-8") as f:
            for link in sample_links:
                f.write(f"{link}\n")
        
        print(f"📁 Sample file '{links_file}' created.")
        print("Please add your Telegram links to this file and run the program again.")
        return
    
    if not chat_links:
        print("❌ No links found in links.txt!")
        return
    
    print(f"📋 Found {len(chat_links)} links to analyze")
    
    # تنظیمات
    try:
        messages_limit = int(input("Enter messages limit per chat (default 1000): ").strip() or "1000")
    except ValueError:
        messages_limit = 1000
    
    # تایید از کاربر
    print(f"\n📊 Analysis Settings:")
    print(f"   • Total links: {len(chat_links)}")
    print(f"   • Messages per chat: {messages_limit}")
    print(f"   • Output file: {os.getenv('OUTPUT_FILE', 'my_chats.json')}")
    
    response = input("\nDo you want to continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Operation cancelled.")
        return
    
    # اجرای تحلیل
    analyzer = TelegramAnalyzer()
    try:
        asyncio.run(analyzer.run_analysis(chat_links, messages_limit))
        
        print("\n🎉 Analysis completed successfully!")
        print(f"📁 Results saved in:")
        print(f"   • {analyzer.output_file} (Main output)")
        print(f"   • results/chat_analysis.json (Chat analysis)")
        print(f"   • results/extracted_links.txt (Extracted links)")
        print(f"   • results/analysis_summary.json (Detailed summary)")
        print(f"   • users/ directory (Individual user files)")
        
    except KeyboardInterrupt:
        print("\n⏹️ Analysis stopped by user")
        # ذخیره نتایج جزئی
        analyzer.save_results_to_files()
        print("💾 Partial results saved.")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    main()
