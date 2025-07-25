import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from utils.logger import logger

@dataclass
class UsernameHistory:
    username: str
    changed_at: str

@dataclass
class NameHistory:
    name: str
    changed_at: str

@dataclass
class JoinedGroup:
    group_id: str
    group_title: str
    joined_at: str
    role: str = "member"
    is_admin: bool = False

@dataclass
class UserMessage:
    group_id: str
    group_title: str
    message_id: int
    text: str
    timestamp: str
    reactions: List[str]
    reply_to: Optional[int] = None
    edited: bool = False
    is_forwarded: bool = False
    media_type: Optional[str] = None

class UserProfile:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.current_username: Optional[str] = None
        self.current_name: Optional[str] = None
        self.username_history: List[UsernameHistory] = []
        self.name_history: List[NameHistory] = []
        self.is_bot: bool = False
        self.is_deleted: bool = False
        self.joined_groups: List[JoinedGroup] = []
        self.messages: List[UserMessage] = []
        self.first_seen: Optional[str] = None
        self.last_seen: Optional[str] = None

    def update_username(self, new_username: str, timestamp: str):
        """بروزرسانی username کاربر"""
        if self.current_username != new_username:
            if self.current_username:  # اگر username قبلی وجود داشت
                self.username_history.append(
                    UsernameHistory(username=self.current_username, changed_at=timestamp)
                )
            self.current_username = new_username

    def update_name(self, new_name: str, timestamp: str):
        """بروزرسانی نام کاربر"""
        if self.current_name != new_name:
            if self.current_name:  # اگر نام قبلی وجود داشت
                self.name_history.append(
                    NameHistory(name=self.current_name, changed_at=timestamp)
                )
            self.current_name = new_name

    def add_group(self, group_id: str, group_title: str, timestamp: str, is_admin: bool = False):
        """اضافه کردن گروه به لیست گروه‌های عضو"""
        # بررسی اینکه آیا قبلاً عضو این گروه بوده یا نه
        existing_group = next((g for g in self.joined_groups if g.group_id == group_id), None)
        if not existing_group:
            role = "admin" if is_admin else "member"
            self.joined_groups.append(
                JoinedGroup(
                    group_id=group_id,
                    group_title=group_title,
                    joined_at=timestamp,
                    role=role,
                    is_admin=is_admin
                )
            )

    def add_message(self, message: UserMessage):
        """اضافه کردن پیام جدید"""
        self.messages.append(message)
        
        # بروزرسانی آخرین بازدید
        self.last_seen = message.timestamp
        
        # تنظیم اولین بازدید اگر وجود نداشته باشد
        if not self.first_seen:
            self.first_seen = message.timestamp

    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای ذخیره در JSON"""
        return {
            "user_id": self.user_id,
            "current_username": self.current_username,
            "current_name": self.current_name,
            "username_history": [asdict(uh) for uh in self.username_history],
            "name_history": [asdict(nh) for nh in self.name_history],
            "is_bot": self.is_bot,
            "is_deleted": self.is_deleted,
            "joined_groups": [asdict(jg) for jg in self.joined_groups],
            "messages": [asdict(msg) for msg in self.messages],
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "total_messages": len(self.messages),
            "total_groups": len(self.joined_groups)
        }

class UserTracker:
    """کلاس اصلی مدیریت و ردیابی کاربران"""
    
    def __init__(self, users_dir: str = "users"):
        self.users_dir = users_dir
        self.users_cache: Dict[int, UserProfile] = {}
        self.ensure_users_directory()

    def ensure_users_directory(self):
        """اطمینان از وجود دایرکتوری users"""
        if not os.path.exists(self.users_dir):
            os.makedirs(self.users_dir)
            logger.info(f"📁 Created users directory: {self.users_dir}")

    def get_user_file_path(self, user_id: int) -> str:
        """دریافت مسیر فایل کاربر"""
        return os.path.join(self.users_dir, f"user_{user_id}.json")

    def load_user(self, user_id: int) -> UserProfile:
        """بارگذاری اطلاعات کاربر از فایل"""
        if user_id in self.users_cache:
            return self.users_cache[user_id]

        file_path = self.get_user_file_path(user_id)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                user_profile = UserProfile(user_id)
                user_profile.current_username = data.get('current_username')
                user_profile.current_name = data.get('current_name')
                user_profile.is_bot = data.get('is_bot', False)
                user_profile.is_deleted = data.get('is_deleted', False)
                user_profile.first_seen = data.get('first_seen')
                user_profile.last_seen = data.get('last_seen')
                
                # بارگذاری تاریخچه username
                for uh_data in data.get('username_history', []):
                    user_profile.username_history.append(
                        UsernameHistory(**uh_data)
                    )
                
                # بارگذاری تاریخچه نام
                for nh_data in data.get('name_history', []):
                    user_profile.name_history.append(
                        NameHistory(**nh_data)
                    )
                
                # بارگذاری گروه‌ها
                for jg_data in data.get('joined_groups', []):
                    user_profile.joined_groups.append(
                        JoinedGroup(**jg_data)
                    )
                
                # بارگذاری پیام‌ها
                for msg_data in data.get('messages', []):
                    user_profile.messages.append(
                        UserMessage(**msg_data)
                    )
                
                self.users_cache[user_id] = user_profile
                return user_profile
                
            except Exception as e:
                logger.error(f"❌ Error loading user {user_id}: {e}")
        
        # اگر فایل وجود نداشت، کاربر جدید ایجاد می‌کنیم
        user_profile = UserProfile(user_id)
        self.users_cache[user_id] = user_profile
        return user_profile

    def process_message(self, message, chat_info):
        """پردازش یک پیام و بروزرسانی اطلاعات کاربر"""
        if not message.from_user:
            return

        user_id = message.from_user.id
        user_profile = self.load_user(user_id)
        
        # بروزرسانی اطلاعات پایه کاربر
        timestamp = message.date.isoformat() if message.date else datetime.now().isoformat()
        
        # بروزرسانی نام کاربری
        current_username = message.from_user.username
        if current_username:
            user_profile.update_username(current_username, timestamp)
        
        # بروزرسانی نام
        full_name = ""
        if message.from_user.first_name:
            full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"
        
        if full_name.strip():
            user_profile.update_name(full_name.strip(), timestamp)
        
        # تنظیم is_bot
        user_profile.is_bot = getattr(message.from_user, 'is_bot', False)
        
        # اضافه کردن گروه
        group_id = str(chat_info.id)
        group_title = chat_info.title or "Unknown Group"
        user_profile.add_group(group_id, group_title, timestamp)
        
        # تشخیص نوع رسانه
        media_type = None
        if message.photo:
            media_type = "photo"
        elif message.video:
            media_type = "video"
        elif message.audio:
            media_type = "audio"
        elif message.document:
            media_type = "document"
        elif message.sticker:
            media_type = "sticker"
        elif message.animation:
            media_type = "animation"
        elif message.voice:
            media_type = "voice"
        elif message.video_note:
            media_type = "video_note"
        
        # اضافه کردن پیام
        user_message = UserMessage(
            group_id=group_id,
            group_title=group_title,
            message_id=message.id,
            text=message.text or message.caption or "",
            timestamp=timestamp,
            reactions=self.extract_reactions(message),
            reply_to=message.reply_to_message.id if message.reply_to_message else None,
            edited=bool(message.edit_date),
            is_forwarded=bool(message.forward_date or message.forward_from),
            media_type=media_type
        )
        
        user_profile.add_message(user_message)
        
        logger.debug(f"👤 Processed message from user {user_id} (@{current_username})")

    def extract_reactions(self, message) -> List[str]:
        """استخراج ری‌اکشن‌ها از پیام"""
        reactions = []
        try:
            if hasattr(message, 'reactions') and message.reactions:
                for reaction in message.reactions.reactions:
                    if hasattr(reaction, 'emoji'):
                        reactions.append(reaction.emoji)
        except:
            pass
        return reactions

    def save_user(self, user_id: int):
        """ذخیره اطلاعات کاربر در فایل"""
        if user_id not in self.users_cache:
            return

        user_profile = self.users_cache[user_id]
        file_path = self.get_user_file_path(user_id)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_profile.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 Saved user {user_id} to {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving user {user_id}: {e}")

    def save_all_users(self):
        """ذخیره همه کاربران"""
        logger.info(f"💾 Saving {len(self.users_cache)} users...")
        
        for user_id in self.users_cache:
            self.save_user(user_id)
        
        logger.info(f"✅ All users saved to {self.users_dir}/")

    def get_statistics(self) -> Dict[str, Any]:
        """دریافت آمار کلی کاربران"""
        total_users = len(self.users_cache)
        total_messages = sum(len(user.messages) for user in self.users_cache.values())
        bot_users = sum(1 for user in self.users_cache.values() if user.is_bot)
        deleted_users = sum(1 for user in self.users_cache.values() if user.is_deleted)
        
        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "bot_users": bot_users,
            "deleted_users": deleted_users,
            "active_users": total_users - deleted_users
        }
