import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from bson import ObjectId
from config.settings import FILE_SETTINGS
from utils.logger import logger

class UserTracker:
    """ردیابی و مدیریت کاربران با ساختار MongoDB"""
    
    def __init__(self):
        self.users: Dict[int, Dict[str, Any]] = {}
        self.user_chats: Dict[int, List[str]] = {}
        self.group_info: Dict[str, Dict[str, Any]] = {}  # اطلاعات گروه‌ها
        
        # ایجاد پوشه users
        self.users_dir = Path(FILE_SETTINGS.users_dir)
        self.users_dir.mkdir(exist_ok=True)
    
    def _generate_object_id(self) -> str:
        """تولید ObjectId برای MongoDB"""
        return str(ObjectId())
    
    def _get_iso_date(self, date_input=None) -> str:
        """تبدیل تاریخ به فرمت ISO"""
        if date_input is None:
            return datetime.now(timezone.utc).isoformat()
        
        if isinstance(date_input, str):
            return date_input
        
        if hasattr(date_input, 'isoformat'):
            if date_input.tzinfo is None:
                date_input = date_input.replace(tzinfo=timezone.utc)
            return date_input.isoformat()
        
        return str(date_input)
    
    def _safe_filename(self, text: str, max_length: int = 50) -> str:
        """ایجاد نام فایل امن"""
        if not text:
            return "unknown"
        
        # حذف کاراکترهای غیرمجاز
        safe_chars = "".join(c for c in text if c.isalnum() or c in "._- ")
        safe_chars = safe_chars.replace(" ", "_")
        
        # محدود کردن طول
        if len(safe_chars) > max_length:
            safe_chars = safe_chars[:max_length]
        
        return safe_chars or "unknown"
    
    def _store_group_info(self, chat_info):
        """ذخیره اطلاعات گروه"""
        try:
            if chat_info is None:
                return
            
            chat_id = str(chat_info.get('id', ''))
            if not chat_id:
                return
            
            group_data = {
                'id': chat_id,
                'title': chat_info.get('title', ''),
                'username': chat_info.get('username', ''),
                'type': chat_info.get('type', ''),
                'description': chat_info.get('description', ''),
                'member_count': chat_info.get('member_count', 0),
                'first_seen': self._get_iso_date()
            }
            
            if chat_id not in self.group_info:
                self.group_info[chat_id] = group_data
            else:
                # به‌روزرسانی اطلاعات موجود
                existing = self.group_info[chat_id]
                for key, value in group_data.items():
                    if key != 'first_seen' and value:
                        existing[key] = value
                        
        except Exception as e:
            logger.error(f"❌ Error storing group info: {e}")
    
    def process_message(self, message, chat_info):
        """پردازش یک پیام و استخراج اطلاعات کاربر"""
        try:
            if message is None or chat_info is None:
                return
            
            # ذخیره اطلاعات گروه
            self._store_group_info(chat_info)
                
            if hasattr(message, 'from_user') and message.from_user:
                user = message.from_user
                self._add_user_message(user, chat_info, message)
            else:
                logger.debug("� Message has no from_user, skipping")
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    def add_user_from_member(self, member, chat_info):
        """اضافه کردن کاربر از ChatMember object"""
        try:
            if member is None or chat_info is None:
                return
            
            # ذخیره اطلاعات گروه
            self._store_group_info(chat_info)
                
            if hasattr(member, 'user') and member.user:
                # بررسی نقش کاربر در گروه
                role = "member"
                is_admin = False
                
                if hasattr(member, 'status'):
                    status = member.status
                    if status in ['administrator', 'creator']:
                        role = "admin"
                        is_admin = True
                    elif status == 'owner':
                        role = "owner"
                        is_admin = True
                
                self._add_user_to_group(member.user, chat_info, role, is_admin)
                
        except Exception as e:
            logger.error(f"❌ Error adding user from member: {e}")
    
    def _add_user_to_group(self, user, chat_info, role="member", is_admin=False):
        """اضافه کردن کاربر به گروه"""
        try:
            if user is None or chat_info is None:
                return
                
            user_id = getattr(user, 'id', None)
            if user_id is None:
                return
            
            chat_id = str(chat_info.get('id', ''))
            if not chat_id:
                return
            
            # ایجاد یا به‌روزرسانی کاربر
            if user_id not in self.users:
                self._create_user_structure(user)
            
            user_data = self.users[user_id]
            
            # به‌روزرسانی اطلاعات کاربری
            self._update_user_info(user_data, user)
            
            # اضافه کردن به گروه‌ها
            group_entry = {
                "group_id": chat_id,
                "group_title": chat_info.get('title', ''),
                "group_username": chat_info.get('username', ''),
                "joined_at": self._get_iso_date(),
                "role": role,
                "is_admin": is_admin
            }
            
            # بررسی اینکه قبلاً در این گروه نباشد
            existing_group = None
            for group in user_data['joined_groups']:
                if group['group_id'] == chat_id:
                    existing_group = group
                    break
            
            if existing_group:
                # به‌روزرسانی نقش اگر تغییر کرده
                existing_group['role'] = role
                existing_group['is_admin'] = is_admin
                existing_group['group_title'] = chat_info.get('title', '')
                existing_group['group_username'] = chat_info.get('username', '')
            else:
                user_data['joined_groups'].append(group_entry)
                
        except Exception as e:
            logger.error(f"❌ Error adding user to group: {e}")
    
    def _add_user_message(self, user, chat_info, message):
        """اضافه کردن پیام کاربر"""
        try:
            if user is None or chat_info is None or message is None:
                return
                
            user_id = getattr(user, 'id', None)
            if user_id is None:
                return
            
            chat_id = str(chat_info.get('id', ''))
            if not chat_id:
                return
            
            # ایجاد یا به‌روزرسانی کاربر
            if user_id not in self.users:
                self._create_user_structure(user)
            
            user_data = self.users[user_id]
            
            # به‌روزرسانی اطلاعات کاربری
            self._update_user_info(user_data, user)
            
            # اطلاعات پیام
            message_entry = {
                "group_id": chat_id,
                "group_title": chat_info.get('title', ''),
                "message_id": getattr(message, 'id', 0),
                "text": getattr(message, 'text', '') or getattr(message, 'caption', '') or '',
                "timestamp": self._get_iso_date(getattr(message, 'date', None)),
                "reactions": self._extract_reactions(message),
                "reply_to": getattr(message, 'reply_to_message_id', None),
                "edited": getattr(message, 'edit_date', None) is not None,
                "is_forwarded": getattr(message, 'forward_date', None) is not None
            }
            
            # حذف مقادیر None
            message_entry = {k: v for k, v in message_entry.items() if v is not None}
            
            user_data['messages'].append(message_entry)
            
            # اطمینان از وجود در گروه
            group_exists = any(g['group_id'] == chat_id for g in user_data['joined_groups'])
            if not group_exists:
                group_entry = {
                    "group_id": chat_id,
                    "group_title": chat_info.get('title', ''),
                    "group_username": chat_info.get('username', ''),
                    "joined_at": self._get_iso_date(),
                    "role": "member",
                    "is_admin": False
                }
                user_data['joined_groups'].append(group_entry)
                
        except Exception as e:
            logger.error(f"❌ Error adding user message: {e}")
    
    def _create_user_structure(self, user):
        """ایجاد ساختار اولیه کاربر"""
        user_id = getattr(user, 'id', None)
        if user_id is None:
            return
        
        # نام کامل کاربر
        first_name = getattr(user, 'first_name', '') or ''
        last_name = getattr(user, 'last_name', '') or ''
        full_name = f"{first_name} {last_name}".strip() or 'Unknown'
        
        # یوزرنیم فعلی
        current_username = getattr(user, 'username', '') or ''
        
        user_structure = {
            "_id": self._generate_object_id(),
            "user_id": user_id,
            "current_username": current_username,
            "current_name": full_name,
            
            "username_history": [],
            "name_history": [],
            
            "is_bot": getattr(user, 'is_bot', False),
            "is_deleted": getattr(user, 'is_deleted', False),
            "is_verified": getattr(user, 'is_verified', False),
            "is_premium": getattr(user, 'is_premium', False),
            "is_scam": getattr(user, 'is_scam', False),
            "is_fake": getattr(user, 'is_fake', False),
            
            "joined_groups": [],
            "messages": [],
            
            # اطلاعات اضافی
            "phone_number": getattr(user, 'phone_number', ''),
            "language_code": getattr(user, 'language_code', ''),
            "dc_id": getattr(user, 'dc_id', None),
            "first_seen": self._get_iso_date(),
            "last_seen": self._get_iso_date()
        }
        
        # اضافه کردن به تاریخچه نام و یوزرنیم
        if full_name and full_name != 'Unknown':
            user_structure["name_history"].append({
                "name": full_name,
                "changed_at": self._get_iso_date()
            })
        
        if current_username:
            user_structure["username_history"].append({
                "username": current_username,
                "changed_at": self._get_iso_date()
            })
        
        self.users[user_id] = user_structure
    
    def _update_user_info(self, user_data, user):
        """به‌روزرسانی اطلاعات کاربر"""
        try:
            # نام کامل جدید
            first_name = getattr(user, 'first_name', '') or ''
            last_name = getattr(user, 'last_name', '') or ''
            new_name = f"{first_name} {last_name}".strip()
            
            # یوزرنیم جدید
            new_username = getattr(user, 'username', '') or ''
            
            # بررسی تغییر نام
            if new_name and new_name != user_data.get('current_name'):
                user_data['current_name'] = new_name
                
                # اضافه کردن به تاریخچه نام
                name_exists = any(
                    entry['name'] == new_name 
                    for entry in user_data['name_history']
                )
                if not name_exists:
                    user_data['name_history'].append({
                        "name": new_name,
                        "changed_at": self._get_iso_date()
                    })
            
            # بررسی تغییر یوزرنیم
            if new_username and new_username != user_data.get('current_username'):
                user_data['current_username'] = new_username
                
                # اضافه کردن به تاریخچه یوزرنیم
                username_exists = any(
                    entry['username'] == new_username 
                    for entry in user_data['username_history']
                )
                if not username_exists:
                    user_data['username_history'].append({
                        "username": new_username,
                        "changed_at": self._get_iso_date()
                    })
            
            # به‌روزرسانی سایر اطلاعات
            user_data['is_bot'] = getattr(user, 'is_bot', False)
            user_data['is_deleted'] = getattr(user, 'is_deleted', False)
            user_data['is_verified'] = getattr(user, 'is_verified', False)
            user_data['is_premium'] = getattr(user, 'is_premium', False)
            user_data['is_scam'] = getattr(user, 'is_scam', False)
            user_data['is_fake'] = getattr(user, 'is_fake', False)
            user_data['last_seen'] = self._get_iso_date()
            
            # به‌روزرسانی سایر فیلدها اگر مقدار جدید دارند
            if getattr(user, 'phone_number', ''):
                user_data['phone_number'] = user.phone_number
            if getattr(user, 'language_code', ''):
                user_data['language_code'] = user.language_code
            if getattr(user, 'dc_id', None):
                user_data['dc_id'] = user.dc_id
                
        except Exception as e:
            logger.error(f"❌ Error updating user info: {e}")
    
    def _extract_reactions(self, message) -> List[str]:
        """استخراج ری‌اکشن‌های پیام"""
        try:
            reactions = []
            
            if hasattr(message, 'reactions') and message.reactions:
                if hasattr(message.reactions, 'results'):
                    for reaction in message.reactions.results:
                        if hasattr(reaction, 'reaction'):
                            if hasattr(reaction.reaction, 'emoticon'):
                                reactions.append(reaction.reaction.emoticon)
                            elif hasattr(reaction.reaction, 'document_id'):
                                # برای استیکرها و ایموجی‌های سفارشی
                                reactions.append(f"custom_{reaction.reaction.document_id}")
            
            return reactions
            
        except Exception as e:
            logger.debug(f"⚠️ Error extracting reactions: {e}")
            return []
    
    def process_messages(self, messages, chat_info):
        """پردازش لیستی از پیام‌ها"""
        logger.info(f"� Processing {len(messages)} messages...")
        
        for message in messages:
            self.process_message(message, chat_info)
        
        logger.info(f"✅ Processed messages. Found {len(self.users)} unique users")
    
    def save_all_users(self, output_file: str = None) -> int:
        """ذخیره تمام کاربران - یک فایل برای هر کاربر در هر گروه"""
        try:
            if not self.users:
                logger.warning("⚠️ No users to save")
                return 0
            
            users_dir = Path(FILE_SETTINGS.users_dir)
            
            try:
                users_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 User directory ready: {users_dir}")
            except Exception as e:
                logger.error(f"❌ Could not create users directory: {e}")
                users_dir = Path.cwd() / "temp_users"
                users_dir.mkdir(parents=True, exist_ok=True)
                logger.warning(f"� Using temporary directory: {users_dir}")
            
            saved_files_count = 0
            total_users = 0
            
            # برای هر کاربر
            for user_id, user_data in self.users.items():
                if user_data is None:
                    continue
                
                total_users += 1
                
                # برای هر گروهی که کاربر عضو است، یک فایل جداگانه
                for group in user_data.get('joined_groups', []):
                    try:
                        group_id = group.get('group_id', '')
                        group_title = group.get('group_title', '')
                        group_username = group.get('group_username', '')
                        
                        if not group_id:
                            continue
                        
                        # تعیین نام گروه برای فایل
                        if group_username:
                            group_name_safe = self._safe_filename(group_username)
                        elif group_title:
                            group_name_safe = self._safe_filename(group_title)
                        else:
                            group_name_safe = "unknown_group"
                        
                        # فرمت نام فایل: {User_id}_{group_id}_{group_name}_users.json
                        filename = f"{user_id}_{group_id}_{group_name_safe}_user.json"
                        file_path = users_dir / filename
                        
                        # فیلتر کردن پیام‌ها برای این گروه خاص
                        group_messages = [
                            msg for msg in user_data.get('messages', [])
                            if msg.get('group_id') == group_id
                        ]
                        
                        # فیلتر کردن اطلاعات گروه برای این گروه خاص
                        current_group_info = [g for g in user_data.get('joined_groups', []) if g.get('group_id') == group_id]
                        
                        # ساختار داده برای این کاربر در این گروه خاص
                        user_in_group = {
                            "_id": user_data["_id"],
                            "user_id": user_data["user_id"],
                            "current_username": user_data["current_username"],
                            "current_name": user_data["current_name"],
                            
                            "username_history": user_data["username_history"],
                            "name_history": user_data["name_history"],
                            
                            "is_bot": user_data["is_bot"],
                            "is_deleted": user_data["is_deleted"],
                            "is_verified": user_data["is_verified"],
                            "is_premium": user_data["is_premium"],
                            "is_scam": user_data["is_scam"],
                            "is_fake": user_data["is_fake"],
                            
                            # فقط اطلاعات مربوط به این گروه
                            "group_info": current_group_info[0] if current_group_info else {},
                            "messages_in_this_group": group_messages,
                            "total_messages_in_group": len(group_messages),
                            
                            # اطلاعات اضافی
                            "phone_number": user_data.get("phone_number", ""),
                            "language_code": user_data.get("language_code", ""),
                            "dc_id": user_data.get("dc_id"),
                            "first_seen": user_data["first_seen"],
                            "last_seen": user_data["last_seen"],
                            
                            # اطلاعات خروجی
                            "export_info": {
                                "export_date": self._get_iso_date(),
                                "group_id": group_id,
                                "group_title": group_title,
                                "group_username": group_username,
                                "format": "MongoDB Compatible"
                            }
                        }
                        
                        # ذخیره فایل JSON
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(user_in_group, f, ensure_ascii=False, indent=2, default=str)
                        
                        # ذخیره فایل BSON format
                        bson_filename = f"{user_id}_{group_id}_{group_name_safe}_user_bson.json"
                        bson_file_path = users_dir / bson_filename
                        
                        bson_format = {
                            "_id": {"$oid": user_data["_id"]},
                            "user_id": user_data["user_id"],
                            "current_username": user_data["current_username"],
                            "current_name": user_data["current_name"],
                            "username_history": [
                                {
                                    "username": item["username"],
                                    "changed_at": {"$date": item["changed_at"]}
                                } for item in user_data["username_history"]
                            ],
                            "name_history": [
                                {
                                    "name": item["name"],
                                    "changed_at": {"$date": item["changed_at"]}
                                } for item in user_data["name_history"]
                            ],
                            "is_bot": user_data["is_bot"],
                            "is_deleted": user_data["is_deleted"],
                            "is_verified": user_data["is_verified"],
                            "is_premium": user_data["is_premium"],
                            "group_info": current_group_info[0] if current_group_info else {},
                            "messages_in_this_group": [
                                {
                                    **msg,
                                    "timestamp": {"$date": msg["timestamp"]}
                                } for msg in group_messages
                            ],
                            "first_seen": {"$date": user_data["first_seen"]},
                            "last_seen": {"$date": user_data["last_seen"]},
                            "export_info": {
                                "export_date": {"$date": self._get_iso_date()},
                                "group_id": group_id,
                                "group_title": group_title,
                                "format": "MongoDB BSON Compatible"
                            }
                        }
                        
                        with open(bson_file_path, 'w', encoding='utf-8') as f:
                            json.dump(bson_format, f, ensure_ascii=False, indent=2)
                        
                        saved_files_count += 2  # JSON + BSON
                        logger.debug(f"💾 Saved use {user_id} in group {group_id} ({group_title or group_username or 'Unknown'})")
                        
                    except Exception as e:
                        logger.error(f"❌ Error saving user {user_id} in group {group_id}: {e}")
            
            # ذخیره فایل خلاصه کلی
            try:
                if output_file:
                    summary_path = users_dir / output_file
                else:
                    summary_path = users_dir / f"summary_all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                summary_data = {
                    "summary": {
                        "export_date": self._get_iso_date(),
                        "total_users": total_users,
                        "total_groups": len(self.group_info),
                        "total_files_created": saved_files_count,
                        "format": "Individual files per user per group"
                    },
                    "groups_info": self.group_info,
                    "statistics": self.get_stats(),
                    "file_naming_pattern": "{User_id}_{group_id}_{group_name}_user.json"
                }
                
                with open(summary_path, 'w', encoding='utf-8') as f:
                    json.dump(summary_data, f, ensure_ascii=False, indent=2, default=str)
                
                logger.info(f"💾 Summar saved to: {summary_path}")
                
            except Exception as e:
                logger.error(f"❌ Error saving summary: {e}")
            
            logger.info(f"🎉 Expor completed! Created {saved_files_count} files for {total_users} users in {len(self.group_info)} groups")
            return saved_files_count
            
        except Exception as e:
            logger.error(f"❌ Error saving users: {e}")
            return 0

    def get_stats(self) -> Dict[str, int]:
        """آمار کاربران"""
        stats = {
            'total_users': len(self.users),
            'total_groups': len(self.group_info),
            'bot_users': 0,
            'deleted_users': 0,
            'verified_users': 0,
            'premium_users': 0,
            'scam_users': 0,
            'fake_users': 0,
            'active_users': 0,
            'users_with_messages': 0,
            'users_in_multiple_groups': 0
        }
        
        for user in self.users.values():
            if user.get('is_bot'):
                stats['bot_users'] += 1
            if user.get('is_deleted'):
                stats['deleted_users'] += 1
            if user.get('is_verified'):
                stats['verified_users'] += 1
            if user.get('is_premium'):
                stats['premium_users'] += 1
            if user.get('is_scam'):
                stats['scam_users'] += 1
            if user.get('is_fake'):
                stats['fake_users'] += 1
            if not user.get('is_deleted') and not user.get('is_bot'):
                stats['active_users'] += 1
            if len(user.get('messages', [])) > 0:
                stats['users_with_messages'] += 1
            if len(user.get('joined_groups', [])) > 1:
                stats['users_in_multiple_groups'] += 1
        
        return stats
    
    def add_user_direct(self, user, chat_info):
        """اضافه کردن کاربر مستقیم"""
        try:
            if user is None or chat_info is None:
                return
            
            # ذخیره اطلاعات گروه
            self._store_group_info(chat_info)
            self._add_user_to_group(user, chat_info)
        except Exception as e:
            logger.error(f"❌ Error adding user direct: {e}")
