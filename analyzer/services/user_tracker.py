import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from bson import ObjectId
from config.settings import FILE_SETTINGS
from utils.logger import logger
from .telegram_storage import TelegramStorage

class UserTracker:
    """ردیابی و مدیریت کاربران با ساختار MongoDB"""
    
    def __init__(self):
        self.users: Dict[int, Dict[str, Any]] = {}
        self.user_chats: Dict[int, List[str]] = {}
        self.group_info: Dict[str, Dict[str, Any]] = {}  # اطلاعات گروه‌ها
        
        # ایجاد پوشه users
        self.users_dir = Path(FILE_SETTINGS.users_dir)
        self.users_dir.mkdir(exist_ok=True)
    
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
    
    def _extract_mentions(self, message) -> Dict[str, List[Any]]:
        """استخراج منشن‌ها از پیام (یوزرنیم‌ها و آی‌دی‌ها در صورت وجود)."""
        mentions_usernames: List[str] = []
        mentions_user_ids: List[int] = []
        try:
            if hasattr(message, 'entities') and message.entities:
                for entity in message.entities:
                    entity_type = getattr(entity, 'type', None)
                    # text mention: اشاره مستقیم به کاربر با آی‌دی
                    if str(entity_type).lower().endswith('text_mention'):
                        user_obj = getattr(entity, 'user', None)
                        if user_obj and hasattr(user_obj, 'id') and user_obj.id is not None:
                            mentions_user_ids.append(user_obj.id)
                    # username mention: @username
                    if str(entity_type).lower().endswith('mention'):
                        # متن پیام را برش دهیم
                        offset = getattr(entity, 'offset', None)
                        length = getattr(entity, 'length', None)
                        text = getattr(message, 'text', None) or getattr(message, 'caption', None)
                        if text is not None and offset is not None and length is not None:
                            handle = text[offset: offset + length]
                            if handle.startswith('@') and len(handle) > 1:
                                mentions_usernames.append(handle[1:])
        except Exception as e:
            logger.debug(f"⚠️ Error extracting mentions: {e}")
        return {
            'mentions_usernames': mentions_usernames,
            'mentions_user_ids': mentions_user_ids
        }

    def _detect_media_type(self, message) -> Optional[str]:
        """تشخیص نوع مدیا از شیٔ پیام Pyrogram"""
        try:
            # ترتیب بررسی مطابق با متداول‌ترین‌ها
            if hasattr(message, 'photo') and getattr(message, 'photo', None) is not None:
                return 'photo'
            if hasattr(message, 'video') and getattr(message, 'video', None) is not None:
                return 'video'
            if hasattr(message, 'voice') and getattr(message, 'voice', None) is not None:
                return 'voice'
            if hasattr(message, 'audio') and getattr(message, 'audio', None) is not None:
                return 'audio'
            if hasattr(message, 'document') and getattr(message, 'document', None) is not None:
                return 'document'
            if hasattr(message, 'sticker') and getattr(message, 'sticker', None) is not None:
                return 'sticker'
            if hasattr(message, 'animation') and getattr(message, 'animation', None) is not None:
                return 'animation'
            if hasattr(message, 'video_note') and getattr(message, 'video_note', None) is not None:
                return 'video_note'
            if hasattr(message, 'contact') and getattr(message, 'contact', None) is not None:
                return 'contact'
            if hasattr(message, 'location') and getattr(message, 'location', None) is not None:
                return 'location'
            if hasattr(message, 'venue') and getattr(message, 'venue', None) is not None:
                return 'venue'
            if hasattr(message, 'poll') and getattr(message, 'poll', None) is not None:
                return 'poll'
            return None
        except Exception:
            return None

    def _compute_reply_info(self, message) -> Dict[str, Any]:
        """محاسبه اطلاعات ریپلای برای یک پیام."""
        try:
            has_parent_obj = hasattr(message, 'reply_to_message') and getattr(message, 'reply_to_message', None) is not None
            parent = getattr(message, 'reply_to_message', None) if has_parent_obj else None
            # تلاش برای استخراج آیدی والد حتی در نبود آبجکت والد
            reply_to_message_id_attr = getattr(message, 'reply_to_message_id', None)
            reply_to_message_id = getattr(parent, 'id', None) if parent else reply_to_message_id_attr
            reply_to_user_id = getattr(parent.from_user, 'id', None) if (parent and getattr(parent, 'from_user', None)) else None

            # تخمین ریشه و عمق با دنبال‌کردن تا چند سطح محدود (اگر parent موجود باشد)
            root_id = getattr(message, 'id', None)
            depth = 0
            if parent:
                current = message
                max_hops = 5
                hops = 0
                while hops < max_hops and hasattr(current, 'reply_to_message') and getattr(current, 'reply_to_message', None) is not None:
                    depth += 1
                    current = current.reply_to_message
                    root_id = getattr(current, 'id', root_id)
                    hops += 1
            elif reply_to_message_id is not None:
                # والد فقط با آیدی شناخته شده است
                root_id = reply_to_message_id
                depth = 1

            # فاصله زمانی با والد
            time_since_parent_sec = None
            if parent and getattr(parent, 'date', None) is not None and getattr(message, 'date', None) is not None:
                try:
                    delta = message.date - parent.date
                    time_since_parent_sec = int(delta.total_seconds())
                except Exception:
                    time_since_parent_sec = None

            parent_media_type = self._detect_media_type(parent) if parent else None

            mentions = self._extract_mentions(message)

            return {
                'has_parent': bool(parent) or (reply_to_message_id is not None),
                'reply_to_message_id': reply_to_message_id,
             #   'reply_to_user_id': reply_to_user_id,
              #  'reply_root_id': root_id,
                'reply_depth': depth,
                'thread_id': root_id,
               # 'position_in_thread': None,  # در مرحله دوم پر می‌شود
                #'time_since_parent_sec': time_since_parent_sec,
               # 'parent_media_type': parent_media_type,
                #'mentions_user_ids': mentions['mentions_user_ids'],
                #'mentions_usernames': mentions['mentions_usernames']
            }
        except Exception as e:
            logger.debug(f"⚠️ Error computing reply info: {e}")
            return {
                'has_parent': False,
                'reply_to_message_id': None,
           #     'reply_to_user_id': None,
            #    'reply_root_id': getattr(message, 'id', None),
                'reply_depth': 0,
                'thread_id': getattr(message, 'id', None),
            #    'position_in_thread': None,
            #    'time_since_parent_sec': None,
                'parent_media_type': None,
             #   'mentions_user_ids': [],
             #   'mentions_usernames': []
            }

    def _compute_media_counts(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """محاسبه تعداد انواع مدیا در بین پیام‌ها"""
        media_type_to_count: Dict[str, int] = {}
        try:
            for message in messages:
                media_type = message.get('media_type')
                if not media_type:
                    continue
                media_type_to_count[media_type] = media_type_to_count.get(media_type, 0) + 1
        except Exception as e:
            logger.debug(f"⚠️ Error computing media counts: {e}")
        return media_type_to_count

    def _index_group_messages(self, group_id: str) -> Dict[str, Any]:
        """ساخت ایندکس پیام‌های یک گروه برای دسترسی سریع به پیام والد و پاسخ‌ها.
        برمی‌گرداند: {
            'by_id': { message_id: summary },
            'replies_by_parent': { parent_message_id: [summary, ...] }
        }
        """
        by_id: Dict[Any, Dict[str, Any]] = {}
        replies_by_parent: Dict[Any, List[Dict[str, Any]]] = {}
        try:
            for other_user in self.users.values():
                other_user_id = other_user.get('user_id')
                other_username = other_user.get('current_username')
                other_name = other_user.get('current_name')
                for m in other_user.get('messages', []):
                    if m.get('group_id') != group_id:
                        continue
                    mid = m.get('message_id')
                    if mid is None:
                        continue
                    summary = {
                        'message_id': mid,
                        'user_id': other_user_id,
                        'username': other_username,
                        'name': other_name,
                        'text': m.get('text', ''),
                        'media_type': m.get('media_type'),
                        'message_link': m.get('message_link'),
                        'timestamp': m.get('timestamp')
                    }
                    by_id[mid] = summary
                    # replies map
                    parent_id = None
                    reply_obj = m.get('reply') or {}
                    parent_id = reply_obj.get('reply_to_message_id')
                    if parent_id is None:
                        parent_id = m.get('reply_to')
                    if parent_id is not None:
                        replies_by_parent.setdefault(parent_id, []).append(summary)
        except Exception as e:
            logger.debug(f"⚠️ Error indexing group messages: {e}")
        return {'by_id': by_id, 'replies_by_parent': replies_by_parent}

    def _compute_thread_positions_and_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """محاسبه position_in_thread برای هر پیام و ساخت آمار thread ها.
        توجه: این محاسبات بر اساس پیام‌های همین کاربر است، نه کل گروه.
        """
        try:
            # گروه‌بندی پیام‌ها بر اساس thread_id
            threads: Dict[Any, List[Dict[str, Any]]] = {}
            for msg in messages:
                reply = msg.get('reply') or {}
                thread_id = reply.get('thread_id') or msg.get('message_id')
                threads.setdefault(thread_id, []).append(msg)

            # مرتب‌سازی هر thread بر اساس زمان و تعیین position
            from datetime import datetime
            def parse_ts(ts: Any) -> datetime:
                if isinstance(ts, str):
                    try:
                        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except Exception:
                        return datetime.min
                return datetime.min

            for thread_id, msgs in threads.items():
                msgs.sort(key=lambda m: parse_ts(m.get('timestamp')))
                for idx, m in enumerate(msgs, start=1):
                    if 'reply' not in m or not isinstance(m['reply'], dict):
                        m['reply'] = {}
                    m['reply']['position_in_thread'] = idx

            # تولید آمار thread ها (در سطح پیام‌های همین کاربر)
            thread_stats = []
            for thread_id, msgs in threads.items():
                if not msgs:
                    continue
                start_ts = parse_ts(msgs[0].get('timestamp'))
                end_ts = parse_ts(msgs[-1].get('timestamp'))
                # unique_users_in_thread در داده‌های کاربر-محور معمولاً 1 است
                unique_users = { }
                for m in msgs:
                    # در ساختار ما اطلاعات نویسنده پیام در سطح کاربر موجود است،
                    # لذا اینجا فقط همان کاربر خواهد بود.
                    unique_users['this_user'] = True

                # محاسبه میانگین فاصله زمانی بین پیام‌های متوالی در این thread
                gaps = []
                for i in range(1, len(msgs)):
                    t_cur = parse_ts(msgs[i].get('timestamp'))
                    t_prev = parse_ts(msgs[i-1].get('timestamp'))
                    gaps.append(int((t_cur - t_prev).total_seconds()))
                avg_gap = int(sum(gaps) / len(gaps)) if gaps else 0

                # آمار مدیا در thread
                media_counts = self._compute_media_counts(msgs)

                thread_stats.append({
                    'thread_id': thread_id,
                    'thread_length': len(msgs),
                    'unique_users_in_thread': len(unique_users),
                    'avg_time_between_replies_sec': avg_gap,
                    'media_in_thread': media_counts,
                    'start_timestamp': msgs[0].get('timestamp'),
                    'end_timestamp': msgs[-1].get('timestamp')
                })

            return {
                'thread_stats': thread_stats
            }
        except Exception as e:
            logger.debug(f"⚠️ Error computing thread positions/stats: {e}")
            return {
                'thread_stats': []
            }

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
                logger.debug("⚠️ Message has no from_user, skipping")
                
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
            
            # ذخیره user_id در دیتابیس
            self._save_user_to_database(user_id)
                
        except Exception as e:
            logger.error(f"❌ Error adding user to group: {e}")
    
    def _save_user_to_database(self, user_id: int):
        """ذخیره user_id در دیتابیس"""
        try:
            # استفاده از asyncio برای اجرای async function در sync context
            import asyncio
            from services.mongo_service import MongoServiceManager
            
            async def save_user_async():
                try:
                    async with MongoServiceManager() as mongo_service:
                        await mongo_service.save_user_id(user_id)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save user {user_id} to database: {e}")
            
            # اجرای async function در event loop موجود یا ایجاد جدید
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # اگر loop در حال اجرا است، از create_task استفاده کن
                    loop.create_task(save_user_async())
                else:
                    # اگر loop در حال اجرا نیست، اجرا کن
                    loop.run_until_complete(save_user_async())
            except RuntimeError:
                # اگر event loop وجود ندارد، ایجاد کن
                asyncio.run(save_user_async())
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to save user {user_id} to database: {e}")
    
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
            
            # تولید لینک پیام
            chat_username = chat_info.get('username', '')
            message_id = getattr(message, 'id', 0)
            message_link = self._generate_message_link(chat_username, message_id)
            
            # تشخیص نوع مدیا
            media_type = self._detect_media_type(message) or ""

            # اطلاعات ریپلای
            reply_to_message_id_safe = None
            try:
                # تلاش برای استخراج ID صحیح والد
                if hasattr(message, 'reply_to_message') and message.reply_to_message is not None:
                    reply_to_message_id_safe = getattr(message.reply_to_message, 'id', None)
                if not reply_to_message_id_safe:
                    reply_to_message_id_safe = getattr(message, 'reply_to_message_id', None)
            except Exception:
                reply_to_message_id_safe = getattr(message, 'reply_to_message_id', None)

            reply_info = self._compute_reply_info(message)

            # اطلاعات پیام
            message_entry = {
                "group_id": chat_id,
                "group_title": chat_info.get('title', ''),
                "message_id": message_id,
                "text": getattr(message, 'text', '') or getattr(message, 'caption', '') or '',
                "timestamp": self._get_iso_date(getattr(message, 'date', None)),
                "reactions": self._extract_reactions(message),
                # مقدار قبلی برای حفظ سازگاری
                "reply_to": reply_to_message_id_safe,
                "edited": getattr(message, 'edit_date', None) is not None,
                "is_forwarded": getattr(message, 'forward_date', None) is not None,
                "message_link": message_link,  # اضافه کردن لینک پیام
                "media_type": media_type,
                "reply": reply_info
            }

            # غنی‌سازی پیام با والد و پاسخ‌ها (در صورت امکان) با استفاده از ایندکس گروه
            try:
                index_map = self._index_group_messages(chat_id)
                by_id = index_map.get('by_id', {})
                replies_by_parent = index_map.get('replies_by_parent', {})

                parent_id = reply_info.get('reply_to_message_id') or reply_to_message_id_safe
                if parent_id in by_id:
                    p = by_id[parent_id]
                    message_entry['parent_message'] = {
                        'message_id': p.get('message_id'),
                        'username': p.get('username'),
                        'text': p.get('text', '')
                    }
                if message_id in replies_by_parent:
                    reps = replies_by_parent.get(message_id, [])
                    message_entry['replies'] = [
                        {
                            'message_id': r.get('message_id'),
                            'username': r.get('username'),
                            'text': r.get('text', '')
                        } for r in reps
                    ]
            except Exception as e:
                logger.debug(f"⚠️ Error enriching message with parent/replies: {e}")
            
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
            
            # ذخیره user_id در دیتابیس
            self._save_user_to_database(user_id)
                
        except Exception as e:
            logger.error(f"❌ Error adding user message: {e}")
    
    def _create_user_structure(self, user):
        """ایجاد ساختار کاربر جدید"""
        try:
            user_id = getattr(user, 'id', None)
            if user_id is None:
                return
            
            # نام کامل اولیه
            first_name = getattr(user, 'first_name', '') or ''
            last_name = getattr(user, 'last_name', '') or ''
            current_name = f"{first_name} {last_name}".strip()
            
            # یوزرنیم اولیه
            current_username = getattr(user, 'username', '') or ''
            
            # ایجاد ساختار کاربر
            user_data = {
                "_id": self._generate_object_id(),
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": current_username,
                "current_name": current_name,
                "current_username": current_username,
                "phone_number": getattr(user, 'phone_number', ''),
                "is_bot": getattr(user, 'is_bot', False),
                "is_verified": getattr(user, 'is_verified', False),
                "is_restricted": getattr(user, 'is_restricted', False),
                "is_scam": getattr(user, 'is_scam', False),
                "is_fake": getattr(user, 'is_fake', False),
                "is_deleted": getattr(user, 'is_deleted', False),
                "is_premium": getattr(user, 'is_premium', False),
                "language_code": getattr(user, 'language_code', ''),
                "dc_id": getattr(user, 'dc_id', None),
                "first_seen": self._get_iso_date(),
                "last_seen": self._get_iso_date(),
                "name_history": [{"name": current_name, "changed_at": self._get_iso_date()}] if current_name else [],
                "username_history": [{"username": current_username, "changed_at": self._get_iso_date()}] if current_username else [],
                "joined_groups": [],
                "messages": [],
                "reactions": [],
                "forwards": [],
                "media_files": [],
                "links": []
            }
            
            self.users[user_id] = user_data
            
            # ذخیره user_id در دیتابیس
            self._save_user_to_database(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error creating user structure: {e}")
    
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

                        # ساخت ایندکس پیام‌های گروه برای افزودن parent/replies
                        index_map = self._index_group_messages(group_id)
                        by_id = index_map.get('by_id', {})
                        replies_by_parent = index_map.get('replies_by_parent', {})
                        for m in group_messages:
                            try:
                                pid = (m.get('reply') or {}).get('reply_to_message_id') or m.get('reply_to')
                                if pid in by_id:
                                    p = by_id[pid]
                                    m['parent_message'] = {
                                        'message_id': p.get('message_id'),
                                        'username': p.get('username'),
                                        'text': p.get('text', '')
                                    }
                                if m.get('message_id') in replies_by_parent:
                                    reps = replies_by_parent.get(m.get('message_id'), [])
                                    m['replies'] = [
                                        {
                                            'message_id': r.get('message_id'),
                                            'username': r.get('username'),
                                            'text': r.get('text', '')
                                        } for r in reps
                                    ]
                            except Exception as e:
                                logger.debug(f"⚠️ Error enriching grouped message: {e}")

                        # حذف خروجی آمار thread ها بر اساس درخواست
                        thread_stats_in_group = []
                        
                        # فیلتر کردن اطلاعات گروه برای این گروه خاص
                        current_group_info = [g for g in user_data.get('joined_groups', []) if g.get('group_id') == group_id]
                        
                        # آمار مدیا برای پیام‌های این گروه
                        media_counts = self._compute_media_counts(group_messages)
                        total_media = sum(media_counts.values())

                        # ساختار داده برای این کاربر در این گروه خاص (به‌همراه پیام‌های والد/پاسخ‌ها)
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
                            # آمار مدیا در این گروه
                            "media_counts_in_group": media_counts,
                            "total_media_in_group": total_media,
                            # (حذف thread_stats_in_group بر اساس درخواست)
                            
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
                            # اضافه کردن آمار مدیا در BSON خلاصه
                            "media_counts_in_group": media_counts,
                            "total_media_in_group": total_media,
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

    async def save_all_users_to_telegram(self, output_file: str = None) -> int:
        """ارسال تمام کاربران به تلگرام - یک فایل برای هر کاربر در هر گروه"""
        try:
            if not self.users:
                logger.warning("⚠️ No users to save")
                return 0
            
            saved_files_count = 0
            total_users = 0
            
            # استفاده از TelegramStorage برای ارسال فایل‌ها
            async with TelegramStorage() as telegram_storage:
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
                            
                            # فیلتر کردن پیام‌ها برای این گروه خاص
                            group_messages = [
                                msg for msg in user_data.get('messages', [])
                                if msg.get('group_id') == group_id
                            ]

                            # حذف خروجی آمار thread ها بر اساس درخواست
                            thread_stats_in_group = []
                            
                            # فیلتر کردن اطلاعات گروه برای این گروه خاص
                            current_group_info = [g for g in user_data.get('joined_groups', []) if g.get('group_id') == group_id]
                            
                            # ساختار داده برای این کاربر در این گروه خاص
                            media_counts = self._compute_media_counts(group_messages)
                            total_media = sum(media_counts.values())
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
                                # آمار مدیا در این گروه
                                "media_counts_in_group": media_counts,
                                "total_media_in_group": total_media,
                                # (حذف thread_stats_in_group بر اساس درخواست)
                                
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
                                    "format": "Telegram Cloud Storage"
                                }
                            }
                            
                            # ارسال فایل JSON به تلگرام
                            group_info = {
                                'group_title': group_title,
                                'group_username': group_username,
                                'group_id': group_id
                            }
                            
                            success = await telegram_storage.send_user_data(user_in_group, user_id, group_info)
                            if success:
                                saved_files_count += 1
                                logger.debug(f"✅ Sent user {user_id} in group {group_id} ({group_title or group_username or 'Unknown'}) to Telegram")
                            else:
                                logger.error(f"❌ Failed to send user {user_id} in group {group_id} to Telegram")
                            
                        except Exception as e:
                            logger.error(f"❌ Error sending user {user_id} in group {group_id}: {e}")
                
                # ارسال فایل خلاصه کلی
                try:
                    summary_data = {
                        "summary": {
                            "export_date": self._get_iso_date(),
                            "total_users": total_users,
                            "total_groups": len(self.group_info),
                            "total_files_created": saved_files_count,
                            "format": "Telegram Cloud Storage"
                        },
                        "groups_info": self.group_info,
                        "statistics": self.get_stats(),
                        "file_naming_pattern": "user_{user_id}_{group_name}_{timestamp}.json"
                    }
                    
                    success = await telegram_storage.send_summary_file(summary_data)
                    if success:
                        logger.info(f"✅ Summary sent to Telegram")
                    else:
                        logger.error(f"❌ Failed to send summary to Telegram")
                    
                except Exception as e:
                    logger.error(f"❌ Error sending summary: {e}")
            
            logger.info(f"🎉 Export completed! Sent {saved_files_count} files for {total_users} users in {len(self.group_info)} groups to Telegram")
            return saved_files_count
            
        except Exception as e:
            logger.error(f"❌ Error saving users to Telegram: {e}")
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