import asyncio
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse, parse_qs, unquote

from pyrogram import Client
from pyrogram.types import Chat, Message, User, ChatPreview
from pyrogram.errors import (
    ChannelPrivate, ChatAdminRequired, FloodWait, 
    UsernameNotOccupied, PeerIdInvalid, InviteHashExpired,
    InviteHashInvalid, UserAlreadyParticipant
)
from pyrogram import raw
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
        self.redirect_mapping: Dict[str, str] = {}  # نگهداری mapping لینک‌های ریدایرکت

    def extract_telegram_link_from_redirect(self, redirect_url: str) -> Optional[str]:
        """استخراج لینک تلگرام اصلی از لینک‌های ریدایرکت"""
        try:
            # Google Translate links
            if 'translate.google.com' in redirect_url:
                parsed = urlparse(redirect_url)
                params = parse_qs(parsed.query)
                
                if 'u' in params:
                    original_url = unquote(params['u'][0])
                    if 't.me' in original_url:
                        return original_url
            
            # سایر انواع ریدایرکت‌ها
            # می‌توانید اینجا انواع دیگر ریدایرکت را اضافه کنید
            
            return None
        except Exception as e:
            logger.error(f"Error extracting from redirect {redirect_url}: {e}")
            return None

    async def resolve_redirect_links(self, links: List[str]) -> List[str]:
        """حل کردن لینک‌های ریدایرکت و استخراج لینک‌های اصلی"""
        resolved_links = []
        
        for link in links:
            if 't.me' in link and 'translate.google.com' not in link:
                # لینک مستقیم تلگرام
                resolved_links.append(link)
                continue
            
            # بررسی اینکه آیا این یک لینک ریدایرکت است
            extracted_link = self.extract_telegram_link_from_redirect(link)
            if extracted_link:
                logger.info(f"🔗 Redirect resolved: {link[:50]}... -> {extracted_link}")
                self.redirect_mapping[link] = extracted_link
                resolved_links.append(extracted_link)
            else:
                # اگر نتوانستیم لینک را استخراج کنیم، آن را به عنوان invalid نگه می‌داریم
                logger.warning(f"⚠️ Could not resolve redirect: {link[:100]}...")
                resolved_links.append(link)  # برای tracking
        
        return resolved_links

    def categorize_telegram_link(self, link: str) -> Dict[str, str]:
        """دسته‌بندی لینک‌های تلگرام"""
        link_info = {
            "original_link": link,
            "type": "unknown",
            "identifier": "",
            "is_invite_link": False,
            "is_redirect": False
        }
        
        # بررسی ریدایرکت
        if link in self.redirect_mapping:
            link_info["is_redirect"] = True
            link_info["redirect_source"] = link
            link = self.redirect_mapping[link]  # استفاده از لینک اصلی
        
        if not 't.me' in link:
            link_info["type"] = "invalid"
            return link_info
        
        try:
            # پاکسازی لینک
            clean_link = link.split('?')[0]  # حذف query parameters
            
            if '/joinchat/' in clean_link:
                # لینک دعوت
                link_info["type"] = "invite_link"
                link_info["is_invite_link"] = True
                # استخراج invite hash
                hash_part = clean_link.split('/joinchat/')[-1]
                link_info["identifier"] = hash_part
                
            elif '/+' in clean_link:
                # فرمت جدید لینک دعوت
                link_info["type"] = "invite_link"
                link_info["is_invite_link"] = True
                hash_part = clean_link.split('/+')[-1]
                link_info["identifier"] = hash_part
                
            else:
                # لینک عمومی با username
                link_info["type"] = "public_link"
                # استخراج username
                username = clean_link.replace("https://t.me/", "").replace("@", "")
                if '/' in username:
                    username = username.split('/')[0]
                link_info["identifier"] = username
                
        except Exception as e:
            logger.error(f"Error categorizing link {link}: {e}")
            link_info["type"] = "invalid"
        
        return link_info

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

    async def analyze_invite_link_advanced(self, invite_hash: str, original_link: str) -> Dict:
        """تحلیل پیشرفته لینک‌های دعوت با استفاده از raw API"""
        result = {
            "link": original_link,
            "type": "invite_link",
            "status": "unknown",
            "title": "",
            "username": "",
            "members_count": 0,
            "chat_id": None,
            "error": None,
            "invite_hash": invite_hash,
            "can_join": False,
            "is_channel": False,
            "is_group": False,
            "is_public": False
        }
        
        try:
            # استفاده از raw API برای چک کردن invite link
            r = await self.app.invoke(
                raw.functions.messages.CheckChatInvite(
                    hash=invite_hash
                )
            )
            
            if isinstance(r, raw.types.ChatInviteAlready):
                # اگر قبلاً عضو شده‌اید یا چت public است
                chat = r.chat
                result["chat_id"] = getattr(chat, 'id', None)
                result["title"] = getattr(chat, 'title', '')
                result["username"] = getattr(chat, 'username', '')
                result["members_count"] = getattr(chat, 'participants_count', 0)
                result["status"] = "accessible"
                result["can_join"] = True
                result["is_public"] = True
                
                # تشخیص نوع چت
                if isinstance(chat, raw.types.Channel):
                    if getattr(chat, 'broadcast', False):
                        result["type"] = "channel_invite"
                        result["is_channel"] = True
                    else:
                        result["type"] = "group_invite" 
                        result["is_group"] = True
                elif isinstance(chat, raw.types.Chat):
                    result["type"] = "group_invite"
                    result["is_group"] = True
                
                # برای چت‌های public، سعی کنیم chat_id را منفی کنیم
                if result["chat_id"] and isinstance(chat, raw.types.Channel):
                    result["chat_id"] = int(f"-100{chat.id}")
                elif result["chat_id"] and isinstance(chat, raw.types.Chat):
                    result["chat_id"] = -chat.id
                    
            elif isinstance(r, raw.types.ChatInvite):
                # چت private است اما اطلاعات محدودی در دسترس است
                result["title"] = getattr(r, 'title', '')
                result["members_count"] = getattr(r, 'participants_count', 0)
                result["status"] = "private"
                result["can_join"] = True
                result["is_public"] = False
                
                # تشخیص نوع
                if getattr(r, 'channel', False):
                    if getattr(r, 'broadcast', False):
                        result["type"] = "channel_invite"
                        result["is_channel"] = True
                    else:
                        result["type"] = "group_invite"
                        result["is_group"] = True
                else:
                    result["type"] = "group_invite"
                    result["is_group"] = True
                    
            else:
                result["error"] = f"Unexpected response type: {type(r)}"
                result["status"] = "error"
                
        except InviteHashExpired:
            result["error"] = "Invite link has expired"
            result["status"] = "expired"
        except InviteHashInvalid:
            result["error"] = "Invalid invite link"
            result["status"] = "invalid"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            logger.error(f"Error analyzing invite link {original_link}: {e}")
            
        return result

    async def analyze_public_link(self, username: str, original_link: str) -> Dict:
        """تحلیل لینک‌های عمومی"""
        result = {
            "link": original_link,
            "type": "unknown",
            "status": "unknown",
            "title": "",
            "username": username,
            "members_count": 0,
            "chat_id": None,
            "error": None,
            "is_channel": False,
            "is_group": False,
            "is_public": True
        }
        
        try:
            chat = await self.app.get_chat(username)
            
            result["title"] = chat.title or ""
            result["username"] = chat.username or ""
            result["members_count"] = getattr(chat, 'members_count', 0)
            result["chat_id"] = chat.id
            
            if chat.type.name == "CHANNEL":
                result["type"] = "channel"
                result["is_channel"] = True
            elif chat.type.name in ["GROUP", "SUPERGROUP"]:
                result["type"] = "group"
                result["is_group"] = True
            elif chat.type.name == "PRIVATE":
                result["type"] = "private"
            
            result["status"] = "public"
            
        except ChannelPrivate:
            result["status"] = "private"
            result["error"] = "Channel/Group is private"
            result["is_public"] = False
        except (UsernameNotOccupied, PeerIdInvalid):
            result["error"] = "Invalid username or link"
            result["status"] = "invalid"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            logger.error(f"Error analyzing public link {original_link}: {e}")
            
        return result

    async def analyze_chat_type(self, chat_link: str) -> Dict:
        """تحلیل نوع چت با پشتیبانی از انواع مختلف لینک"""
        
        # دسته‌بندی لینک
        link_info = self.categorize_telegram_link(chat_link)
        
        if link_info["type"] == "invalid":
            return {
                "link": chat_link,
                "type": "invalid",
                "status": "invalid",
                "title": "",
                "username": "",
                "members_count": 0,
                "chat_id": None,
                "error": "Invalid or non-Telegram link",
                "link_category": "invalid",
                "is_channel": False,
                "is_group": False,
                "is_public": False
            }
        
        # تحلیل بر اساس نوع لینک
        if link_info["is_invite_link"]:
            result = await self.analyze_invite_link_advanced(link_info["identifier"], chat_link)
        else:
            result = await self.analyze_public_link(link_info["identifier"], chat_link)
        
        # اضافه کردن اطلاعات دسته‌بندی
        result["link_category"] = link_info["type"]
        result["is_redirect"] = link_info.get("is_redirect", False)
        
        if link_info.get("is_redirect"):
            result["redirect_source"] = link_info.get("redirect_source", "")
        
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
        # فقط چت‌هایی که قابل دسترسی هستند
        accessible_statuses = ["public", "accessible"]
        if chat_info["status"] not in accessible_statuses or chat_info.get("error"):
            logger.warning(f"⏭️ Skipping chat: {chat_link[:50]}... - Status: {chat_info['status']} - {chat_info.get('error', 'Not accessible')}")
            return
        
        try:
            chat_id = chat_info["chat_id"]
            chat_title = chat_info["title"]
            
            if not chat_id:
                logger.warning(f"⏭️ No chat_id for: {chat_title}")
                return
            
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
        
        # 1. ذخیره تحلیل چت‌ها با جزئیات بیشتر
        detailed_analysis = {
            "analysis_metadata": {
                "total_links": len(self.chat_analysis_results),
                "analysis_date": datetime.utcnow().isoformat(),
                "link_categories": {}
            },
            "redirect_mappings": self.redirect_mapping,
            "chats": self.chat_analysis_results
        }
        
        # آمار دسته‌بندی لینک‌ها
        categories = {}
        for chat in self.chat_analysis_results:
            category = chat.get("link_category", "unknown")
            categories[category] = categories.get(category, 0) + 1
        
        detailed_analysis["analysis_metadata"]["link_categories"] = categories
        
        with open("results/chat_analysis.json", "w", encoding="utf-8") as f:
            json.dump(detailed_analysis, f, ensure_ascii=False, indent=2)
        
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
                "accessible_chats": len([c for c in self.chat_analysis_results if c["status"] in ["public", "accessible"]]),
                "private_chats": len([c for c in self.chat_analysis_results if c["status"] == "private"]),
                "invalid_chats": len([c for c in self.chat_analysis_results if c["status"] == "invalid"]),
                "expired_invites": len([c for c in self.chat_analysis_results if c["status"] == "expired"]),
                "redirect_links": len([c for c in self.chat_analysis_results if c.get("is_redirect", False)]),
                "total_users": len(self.processed_users),
                "total_extracted_links": len(self.extracted_links),
                "analysis_date": datetime.utcnow().isoformat()
            },
            "chat_types": {
                "channels": len([c for c in self.chat_analysis_results if c.get("is_channel", False)]),
                "groups": len([c for c in self.chat_analysis_results if c.get("is_group", False)]),
                "invite_links": len([c for c in self.chat_analysis_results if c.get("link_category") == "invite_link"]),
                "public_links": len([c for c in self.chat_analysis_results if c.get("link_category") == "public_link"]),
                "public_chats": len([c for c in self.chat_analysis_results if c.get("is_public", False)]),
                "unknown": len([c for c in self.chat_analysis_results if c.get("type") == "unknown"])
            },
            "link_categories": categories,
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
        logger.info(f"   • Total links: {len(self.chat_analysis_results)}")
        logger.info(f"   • Accessible chats: {summary['analysis_info']['accessible_chats']}")
        logger.info(f"   • Private chats: {summary['analysis_info']['private_chats']}")
        logger.info(f"   • Invalid/expired: {summary['analysis_info']['invalid_chats'] + summary['analysis_info']['expired_invites']}")
        logger.info(f"   • Redirect links resolved: {summary['analysis_info']['redirect_links']}")
        logger.info(f"   • Total users: {len(self.processed_users)}")
        logger.info(f"   • Extracted links: {len(self.extracted_links)}")
        
        # آمار دسته‌بندی
        logger.info("📋 Link Categories:")
        for category, count in categories.items():
            logger.info(f"   • {category}: {count}")

    async def run_analysis(self, chat_links: List[str], messages_per_chat: int = 1000):
        """اجرای تحلیل کامل"""
        async with self.app:
            logger.info("🚀 Starting Telegram analysis...")
            logger.info(f"📋 Total links to analyze: {len(chat_links)}")
            
            # مرحله 0: حل کردن لینک‌های ریدایرکت
            logger.info("🔗 Phase 0: Resolving redirect links...")
            resolved_links = await self.resolve_redirect_links(chat_links)
            
            # مرحله 1: تحلیل نوع چت‌ها
            logger.info("🔍 Phase 1: Analyzing chat types...")
            for i, link in enumerate(resolved_links, 1):
                logger.info(f"   [{i}/{len(resolved_links)}] {link[:80]}...")
                result = await self.analyze_chat_type(link)
                self.chat_analysis_results.append(result)
                
                # ذخیره فوری نتایج
                with open("results/chat_analysis_partial.json", "w", encoding="utf-8") as f:
                    json.dump(self.chat_analysis_results, f, ensure_ascii=False, indent=2)
                
                await asyncio.sleep(1)  # جلوگیری از flood
            
            # مرحله 2: تحلیل پیام‌ها
            accessible_chats = [r for r in self.chat_analysis_results if r["status"] in ["public", "accessible"]]
            logger.info(f"📥 Phase 2: Analyzing messages from {len(accessible_chats)} accessible chats...")
            
            for i, chat_info in enumerate(accessible_chats, 1):
                logger.info(f"   [{i}/{len(accessible_chats)}] Processing: {chat_info.get('title', chat_info['link'][:50])}")
                await self.analyze_chat_messages(chat_info["link"], chat_info, messages_per_chat)
                
                # ذخیره میانی
                if i % 3 == 0:  # هر 3 چت یکبار ذخیره کن
                    logger.info("💾 Saving intermediate results...")
                    self.save_results_to_files()
            
            # مرحله 3: ذخیره نتایج نهایی
            logger.info("💾 Phase 3: Saving final results...")
            self.save_results_to_files()
            
            logger.info("✅ Analysis completed successfully!")

def main():
    """تابع اصلی"""
    # خواندن لینک‌ها از فایل
    links_file = os.getenv('LINKS_FILE', 'links.txt')
    messages_per_chat = int(os.getenv('MESSAGES_PER_CHAT', '1000'))
    
    if not os.path.exists(links_file):
        logger.error(f"❌ Links file not found: {links_file}")
        print("Creating sample links.txt file...")
        with open(links_file, 'w', encoding='utf-8') as f:
            f.write("# Add your Telegram links here, one per line\n")
            f.write("# Examples:\n")
            f.write("# https://t.me/joinchat/abc123\n")
            f.write("# https://t.me/channelname\n")
            f.write("# @username\n")
        print(f"✅ Created {links_file}. Please add your links and run again.")
        return
    
    # خواندن لینک‌ها
    chat_links = []
    try:
        with open(links_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    chat_links.append(line)
        
        if not chat_links:
            logger.error("❌ No valid links found in links.txt")
            return
            
        logger.info(f"📋 Loaded {len(chat_links)} links from {links_file}")
        
    except Exception as e:
        logger.error(f"❌ Error reading links file: {e}")
        return
    
    # اجرای تحلیل
    analyzer = TelegramAnalyzer()
    try:
        asyncio.run(analyzer.run_analysis(chat_links, messages_per_chat))
    except KeyboardInterrupt:
        logger.info("⏹️ Analysis interrupted by user")
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()
