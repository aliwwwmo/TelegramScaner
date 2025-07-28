import asyncio
from datetime import datetime
from typing import Dict, List, Set

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from models.data_models import GroupInfo
from services.link_analyzer import LinkAnalyzer
from config.settings import FILTER_SETTINGS
from utils.logger import logger

class MessageAnalyzer:
    """کلاس تحلیل پیام‌ها"""
    
    def __init__(self, client: Client, link_analyzer: LinkAnalyzer):
        self.client = client
        self.link_analyzer = link_analyzer
        self.processed_users: Dict[int, Dict] = {}
        self.extracted_links: Set[str] = set()
    
    def _should_skip_message(self, message: Message) -> bool:
        """بررسی اینکه آیا پیام باید رد شود یا نه"""
        # بررسی پیام‌های اسکن
        if message.text and FILTER_SETTINGS.filter_scan_messages:
            text_lower = message.text.lower().strip()
            # فیلتر کردن پیام‌های مربوط به شروع اسکن
            if any(keyword in text_lower for keyword in FILTER_SETTINGS.scan_keywords):
                logger.info(f"⏭️ Skipping scan start message: {message.id}")
                return True
            
            # فیلتر کردن پیام‌های سیستم
            if message.from_user and message.from_user.is_bot and FILTER_SETTINGS.filter_bot_messages:
                if any(keyword in text_lower for keyword in FILTER_SETTINGS.bot_keywords):
                    logger.info(f"⏭️ Skipping bot/system message: {message.id}")
                    return True
        
        return False
    
    def _generate_message_link(self, chat_username: str, message_id: int) -> str:
        """تولید لینک پیام تلگرام"""
        try:
            if not chat_username or not message_id:
                return ""
            
            # حذف @ از ابتدای username اگر وجود داشته باشد
            username = chat_username.lstrip('@')
            
            # تولید لینک پیام
            message_link = f"https://t.me/{username}/{message_id}"
            return message_link
            
        except Exception as e:
            logger.error(f"❌ Error generating message link: {e}")
            return ""
    
    async def process_user_message(self, message: Message, group_id: str, group_title: str = ""):
        """پردازش پیام کاربر و ذخیره اطلاعات"""
        # بررسی اینکه آیا پیام باید رد شود
        if self._should_skip_message(message):
            return
            
        if not message.from_user:
            return
            
        user = message.from_user
        user_id = user.id
        
        # اگر کاربر جدید است، ایجاد رکورد اولیه
        if user_id not in self.processed_users:
            self.processed_users[user_id] = {
                'user_id': user_id,
                'current_username': user.username,
                'current_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'is_bot': user.is_bot or False,
                'is_deleted': user.is_deleted or False,
                'joined_groups': [],
                'messages': []
            }
        
        user_data = self.processed_users[user_id]
        
        # بروزرسانی username اگر تغییر کرده
        if user.username and user.username != user_data['current_username']:
            user_data['current_username'] = user.username
        
        # بروزرسانی نام اگر تغییر کرده
        current_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if current_name and current_name != user_data['current_name']:
            user_data['current_name'] = current_name
        
        # اضافه کردن گروه به لیست گروه‌های عضو شده (اگر وجود نداشته باشد)
        group_exists = any(g.get('group_id') == group_id for g in user_data['joined_groups'])
        if not group_exists:
            group_info = {
                'group_id': group_id,
                'group_title': group_title,
                'joined_at': datetime.utcnow().isoformat()
            }
            user_data['joined_groups'].append(group_info)
        
        # تولید لینک پیام
        chat_username = ""
        if hasattr(message, 'chat') and message.chat:
            chat_username = getattr(message.chat, 'username', '')
        
        message_id = message.id
        message_link = self._generate_message_link(chat_username, message_id)
        
        # اضافه کردن پیام
        reactions = []
        if hasattr(message, 'reactions') and message.reactions:
            for reaction in message.reactions.reactions:
                reactions.append(reaction.emoji)
        
        message_data = {
            'group_id': group_id,
            'message_id': message_id,
            'text': message.text or "",
            'timestamp': message.date.isoformat(),
            'reactions': reactions,
            'reply_to': message.reply_to_message.id if message.reply_to_message else None,
            'edited': message.edit_date is not None,
            'is_forwarded': message.forward_from is not None,
            'message_link': message_link
        }
        
        user_data['messages'].append(message_data)
        
        # استخراج لینک‌ها از متن پیام
        if message.text:
            links = self.link_analyzer.extract_links_from_text(message.text)
            self.extracted_links.update(links)
    
    def get_stats(self) -> Dict:
        """دریافت آمار پردازش شده"""
        total_users = len(self.processed_users)
        bot_users = sum(1 for u in self.processed_users.values() if u.get('is_bot', False))
        deleted_users = sum(1 for u in self.processed_users.values() if u.get('is_deleted', False))
        active_users = total_users - bot_users - deleted_users
        
        return {
            'total_users': total_users,
            'bot_users': bot_users,
            'deleted_users': deleted_users,
            'active_users': active_users,
            'extracted_links_count': len(self.extracted_links)
        }
