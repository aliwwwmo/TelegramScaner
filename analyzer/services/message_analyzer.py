import asyncio
from datetime import datetime
from typing import Dict, List

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from models.data_models import UserData, MessageData, GroupInfo, ChatAnalysisResult
from services.link_analyzer import LinkAnalyzer
from utils.logger import logger

class MessageAnalyzer:
    """کلاس تحلیل پیام‌ها"""
    
    def __init__(self, client: Client, link_analyzer: LinkAnalyzer):
        self.client = client
        self.link_analyzer = link_analyzer
        self.processed_users: Dict[int, UserData] = {}
        self.extracted_links = set()
    
    async def process_user_message(self, message: Message, group_id: str, group_title: str = ""):
        """پردازش پیام کاربر و ذخیره اطلاعات"""
        if not message.from_user:
            return
            
        user = message.from_user
        user_id = user.id
        
        # اگر کاربر جدید است، ایجاد رکورد اولیه
        if user_id not in self.processed_users:
            self.processed_users[user_id] = UserData(
                user_id=user_id,
                current_username=user.username,
                current_name=f"{user.first_name or ''} {user.last_name or ''}".strip(),
                is_bot=user.is_bot or False,
                is_deleted=user.is_deleted or False
            )
        
        user_data = self.processed_users[user_id]
        
        # بروزرسانی username اگر تغییر کرده
        if user.username and user.username != user_data.current_username:
            if user_data.current_username:
                user_data.username_history.append({
                    "username": user_data.current_username,
                    "changed_at": datetime.utcnow().isoformat()
                })
            user_data.current_username = user.username
        
        # بروزرسانی نام اگر تغییر کرده
        current_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if current_name and current_name != user_data.current_name:
            if user_data.current_name:
                user_data.name_history.append({
                    "name": user_data.current_name,
                    "changed_at": datetime.utcnow().isoformat()
                })
            user_data.current_name = current_name
        
        # اضافه کردن گروه به لیست گروه‌های عضو شده (اگر وجود نداشته باشد)
        group_exists = any(g.group_id == group_id for g in user_data.joined_groups)
        if not group_exists:
            group_info = GroupInfo(
                group_id=group_id,
                group_title=group_title,
                joined_at=datetime.utcnow().isoformat()
            )
            user_data.joined_groups.append(group_info)
        
        # اضافه کردن پیام
        reactions = []
        if hasattr(message, 'reactions') and message.reactions:
            for reaction in message.reactions.reactions:
                reactions.append(reaction.emoji)
        
        message_data = MessageData(
            group_id=group_id,
            message_id=message.id,
            text=message.text or message.caption or "",
            timestamp=message.date.isoformat() if message.date else datetime.utcnow().isoformat(),
            reactions=reactions,
            reply_to=message.reply_to_message_id,
            edited=bool(message.edit_date),
            is_forwarded=bool(message.forward_date)
        )
        
        user_data.messages.append(message_data)
    
    async def analyze_chat_messages(self, chat_info: ChatAnalysisResult, limit: int = 1000):
        """تحلیل پیام‌های چت و استخراج لینک‌ها"""
        # فقط چت‌هایی که قابل دسترسی هستند
        accessible_statuses = ["public", "accessible"]
        if chat_info.status not in accessible_statuses or chat_info.error:
            logger.warning(f"⏭️ Skipping chat: {chat_info.link[:50]}... - Status: {chat_info.status} - {chat_info.error or 'Not accessible'}")
            return
        
        try:
            chat_id = chat_info.chat_id
            chat_title = chat_info.title
            
            if not chat_id:
                logger.warning(f"⏭️ No chat_id for: {chat_title}")
                return
            
            logger.info(f"📥 Analyzing messages in: {chat_title} (limit: {limit})")
            
            message_count = 0
            async for message in self.client.get_chat_history(chat_id, limit=limit):
                message_count += 1
                
                # پردازش کاربر پیام
                await self.process_user_message(message, str(chat_id), chat_title)
                
                # استخراج لینک‌ها از متن پیام
                text = message.text or message.caption or ""
                links = self.link_analyzer.extract_links_from_text(text)
                
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
            logger.error(f"❌ Error analyzing chat {chat_info.link}: {e}")
