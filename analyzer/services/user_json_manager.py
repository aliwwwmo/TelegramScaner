import json
import os
import asyncio
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from config.settings import TELEGRAM_CONFIG
from utils.logger import logger

class UserJSONManager:
    """مدیریت فایل‌های JSON کاربران از Saved Messages"""
    
    def __init__(self):
        self.api_id = TELEGRAM_CONFIG.api_id
        self.api_hash = TELEGRAM_CONFIG.api_hash
        self.session_string = TELEGRAM_CONFIG.session_string
        self.client = None
        
    async def __aenter__(self):
        """شروع کلاینت تلگرام"""
        try:
            self.client = Client(
                "user_json_manager",
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_string=self.session_string
            )
            await self.client.start()
            
            # استفاده از Saved Messages
            me = await self.client.get_me()
            self.target_chat_id = me.id
            logger.info(f"✅ Connected to Saved Messages (ID: {self.target_chat_id})")
            
            return self
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram client: {e}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """توقف کلاینت تلگرام"""
        if self.client:
            await self.client.stop()
            logger.info("🛑 Telegram client stopped")
    
    def extract_user_id_from_filename(self, filename: str) -> Optional[int]:
        """استخراج user_id از نام فایل"""
        try:
            # الگوی ساده‌تر برای فایل‌های مختلف
            patterns = [
                # الگوی اصلی: temp_user_id_group_id_timestamp_uuid.json
                r'^temp_(\d+)_[^_]+_\d{8}_\d{6}_[a-f0-9]{8}\.json$',
                # الگوی با group_id منفی: temp_user_id_-group_id_timestamp_uuid.json
                r'^temp_(\d+)_-?\d+_\d{8}_\d{6}_[a-f0-9]{8}\.json$',
                # الگوی بدون temp_: user_id_group_id_timestamp_uuid.json
                r'^(\d+)_[^_]+_\d{8}_\d{6}_[a-f0-9]{8}\.json$',
                # الگوی بدون temp_ و group_id منفی: user_id_-group_id_timestamp_uuid.json
                r'^(\d+)_-?\d+_\d{8}_\d{6}_[a-f0-9]{8}\.json$',
                # الگوی عمومی‌تر: هر فایلی که با temp_ شروع شود و user_id داشته باشد
                r'^temp_(\d+)_[^_]*\.json$',
                # الگوی عمومی‌تر: هر فایلی که user_id داشته باشد
                r'^(\d+)_[^_]*\.json$',
                # الگوی خیلی ساده: هر فایلی که با temp_ شروع شود و عدد داشته باشد
                r'^temp_(\d+)_.*\.json$',
                # الگوی خیلی ساده: هر فایلی که با عدد شروع شود
                r'^(\d+)_.*\.json$'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, filename)
                if match:
                    user_id = int(match.group(1))
                    logger.info(f"✅ Extracted user_id {user_id} from {filename} using pattern: {pattern}")
                    return user_id
            
            logger.info(f"❌ No pattern matched for filename: {filename}")
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting user_id from filename {filename}: {e}")
            return None
    
    def extract_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """استخراج timestamp از نام فایل"""
        try:
            # الگوی ساده‌تر برای timestamp
            patterns = [
                # الگوی اصلی: temp_user_id_group_id_YYYYMMDD_HHMMSS_uuid.json
                r'^temp_\d+_[^_]+_(\d{8}_\d{6})_[a-f0-9]{8}\.json$',
                # الگوی با group_id منفی: temp_user_id_-group_id_YYYYMMDD_HHMMSS_uuid.json
                r'^temp_\d+_-?\d+_(\d{8}_\d{6})_[a-f0-9]{8}\.json$',
                # الگوی بدون temp_: user_id_group_id_YYYYMMDD_HHMMSS_uuid.json
                r'^\d+_[^_]+_(\d{8}_\d{6})_[a-f0-9]{8}\.json$',
                # الگوی بدون temp_ و group_id منفی: user_id_-group_id_YYYYMMDD_HHMMSS_uuid.json
                r'^\d+_-?\d+_(\d{8}_\d{6})_[a-f0-9]{8}\.json$',
                # الگوی عمومی‌تر: هر فایلی که timestamp داشته باشد
                r'.*_(\d{8}_\d{6})_[a-f0-9]{8}\.json$'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, filename)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        return datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    except ValueError:
                        logger.debug(f"❌ Invalid timestamp format: {timestamp_str}")
                        continue
            
            logger.debug(f"❌ No timestamp found in filename: {filename}")
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting timestamp from filename {filename}: {e}")
            return None
    
    async def get_user_json_files(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت تمام فایل‌های JSON مربوط به یک کاربر"""
        try:
            user_files = []
            all_files = []
            
            # دریافت تمام پیام‌های Saved Messages
            async for message in self.client.get_chat_history(self.target_chat_id, limit=1000):
                try:
                    # بررسی اینکه آیا پیام شامل فایل است
                    if message.document and message.document.file_name:
                        filename = message.document.file_name
                        all_files.append(filename)
                        
                        # بررسی اینکه آیا فایل مربوط به کاربر مورد نظر است
                        file_user_id = self.extract_user_id_from_filename(filename)
                        if file_user_id == user_id:
                            file_info = {
                                'message_id': message.id,
                                'filename': filename,
                                'file_id': message.document.file_id,
                                'file_size': message.document.file_size,
                                'timestamp': self.extract_timestamp_from_filename(filename),
                                'date': message.date,
                                'caption': None  # حذف caption برای جلوگیری از خطا
                            }
                            user_files.append(file_info)
                except Exception as e:
                    logger.warning(f"⚠️ Error processing message: {e}")
                    continue
            
            # مرتب کردن بر اساس timestamp
            user_files.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min)
            
            logger.info(f"✅ Found {len(user_files)} JSON files for user {user_id}")
            
            # نمایش فایل‌های JSON موجود برای debug
            json_files = [f for f in all_files if f.endswith('.json')]
            logger.info(f"📁 Total JSON files found: {len(json_files)}")
            if json_files:
                logger.info("📋 Sample JSON files:")
                for filename in json_files[:5]:  # نمایش 5 فایل اول
                    extracted_id = self.extract_user_id_from_filename(filename)
                    logger.info(f"   - {filename} (extracted user_id: {extracted_id})")
            
            return user_files
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Error getting user JSON files: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    async def download_and_parse_json(self, file_id: str) -> Optional[Dict[str, Any]]:
        """دانلود و پارس کردن فایل JSON"""
        try:
            # دانلود فایل
            temp_file = await self.client.download_media(file_id)
            
            if not temp_file or not os.path.exists(temp_file):
                logger.error(f"❌ Failed to download file: {file_id}")
                return None
            
            # خواندن و پارس کردن JSON
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # حذف فایل موقت
            os.remove(temp_file)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error downloading/parsing JSON file: {e}")
            return None
    
    async def merge_user_json_files(self, user_id: int) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """ترکیب تمام فایل‌های JSON یک کاربر"""
        try:
            # دریافت تمام فایل‌های کاربر
            user_files = await self.get_user_json_files(user_id)
            
            if not user_files:
                logger.warning(f"⚠️ No JSON files found for user {user_id}")
                return False, None, None
            
            # بررسی اینکه آیا فایل نهایی قبلاً وجود دارد
            final_filename = None
            final_file_data = None
            
            # جستجوی فایل نهایی (با پیشوند final_)
            for file_info in user_files:
                if file_info['filename'].startswith(f'final_{user_id}_'):
                    final_filename = file_info['filename']
                    final_file_data = await self.download_and_parse_json(file_info['file_id'])
                    break
            
            # اگر فایل نهایی وجود دارد، بررسی فایل‌های جدید
            if final_file_data:
                final_timestamp = self.extract_timestamp_from_filename(final_filename)
                new_files = []
                
                for file_info in user_files:
                    if not file_info['filename'].startswith('final_'):
                        file_timestamp = file_info['timestamp']
                        if file_timestamp and file_timestamp > final_timestamp:
                            new_files.append(file_info)
                
                if not new_files:
                    logger.info(f"✅ No new files found for user {user_id}, returning existing final file")
                    return True, final_file_data, final_filename
                
                # ترکیب فایل نهایی با فایل‌های جدید
                merged_data = final_file_data.copy()
                merged_messages = merged_data.get('messages', [])
                
                for file_info in new_files:
                    file_data = await self.download_and_parse_json(file_info['file_id'])
                    if file_data:
                        new_messages = file_data.get('messages', [])
                        merged_messages.extend(new_messages)
                
                merged_data['messages'] = merged_messages
                merged_data['total_files_merged'] = len(new_files) + 1
                merged_data['last_merge_date'] = datetime.now().isoformat()
                
            else:
                # ترکیب تمام فایل‌ها
                merged_data = {
                    'user_id': user_id,
                    'merge_date': datetime.now().isoformat(),
                    'total_files_merged': len(user_files),
                    'messages': [],
                    'user_info': {},
                    'groups_info': []
                }
                
                # برای جلوگیری از تکرار پیام‌ها
                seen_message_ids = set()
                user_info_found = False
                groups_info = {}
                
                # برای ترکیب تاریخچه username و name
                username_history = {}
                name_history = {}
                
                processed_files = 0
                for file_info in user_files:
                    # پردازش تمام فایل‌ها (نه فقط فایل‌های final_)
                    file_data = await self.download_and_parse_json(file_info['file_id'])
                    if file_data:
                        # استخراج اطلاعات کاربر
                        if not user_info_found and 'current_username' in file_data:
                            merged_data['user_info'] = {
                                'current_username': file_data.get('current_username'),
                                'current_name': file_data.get('current_name'),
                                'username_history': file_data.get('username_history', []),
                                'name_history': file_data.get('name_history', []),
                                'is_bot': file_data.get('is_bot', False),
                                'is_deleted': file_data.get('is_deleted', False),
                                'is_verified': file_data.get('is_verified', False),
                                'is_premium': file_data.get('is_premium', False),
                                'is_scam': file_data.get('is_scam', False),
                                'is_fake': file_data.get('is_fake', False),
                                'phone_number': file_data.get('phone_number'),
                                'language_code': file_data.get('language_code'),
                                'dc_id': file_data.get('dc_id'),
                                'first_seen': file_data.get('first_seen'),
                                'last_seen': file_data.get('last_seen')
                            }
                            user_info_found = True
                            logger.info(f"📋 Found user info: {file_data.get('current_username', 'unknown')}")
                        
                        # ترکیب تاریخچه username
                        if 'username_history' in file_data:
                            for username_entry in file_data['username_history']:
                                username = username_entry.get('username')
                                changed_at = username_entry.get('changed_at')
                                if username and changed_at:
                                    if username not in username_history or changed_at > username_history[username]:
                                        username_history[username] = changed_at
                        
                        # ترکیب تاریخچه name
                        if 'name_history' in file_data:
                            for name_entry in file_data['name_history']:
                                name = name_entry.get('name')
                                changed_at = name_entry.get('changed_at')
                                if name and changed_at:
                                    if name not in name_history or changed_at > name_history[name]:
                                        name_history[name] = changed_at
                        
                        # استخراج اطلاعات گروه
                        if 'group_info' in file_data:
                            group_info = file_data['group_info']
                            group_id = group_info.get('group_id')
                            if group_id and group_id not in groups_info:
                                groups_info[group_id] = group_info
                                logger.info(f"📁 Found group info: {group_info.get('group_title', 'unknown')}")
                        
                        # پردازش پیام‌ها بدون تکرار
                        messages_to_add = []
                        if 'messages' in file_data:
                            messages = file_data.get('messages', [])
                        elif 'messages_in_this_group' in file_data:
                            messages = file_data.get('messages_in_this_group', [])
                        else:
                            messages = []
                        
                        for message in messages:
                            message_id = message.get('message_id')
                            if message_id and message_id not in seen_message_ids:
                                seen_message_ids.add(message_id)
                                messages_to_add.append(message)
                        
                        merged_data['messages'].extend(messages_to_add)
                        logger.info(f"📄 Added {len(messages_to_add)} unique messages from {file_info['filename']}")
                        processed_files += 1
                
                # تبدیل groups_info به لیست
                merged_data['groups_info'] = list(groups_info.values())
                
                # به‌روزرسانی تاریخچه‌ها در user_info
                if merged_data['user_info']:
                    # تبدیل username_history به لیست
                    username_history_list = []
                    for username, changed_at in username_history.items():
                        username_history_list.append({
                            'username': username,
                            'changed_at': changed_at
                        })
                    # مرتب کردن بر اساس تاریخ
                    username_history_list.sort(key=lambda x: x['changed_at'])
                    merged_data['user_info']['username_history'] = username_history_list
                    
                    # تبدیل name_history به لیست
                    name_history_list = []
                    for name, changed_at in name_history.items():
                        name_history_list.append({
                            'name': name,
                            'changed_at': changed_at
                        })
                    # مرتب کردن بر اساس تاریخ
                    name_history_list.sort(key=lambda x: x['changed_at'])
                    merged_data['user_info']['name_history'] = name_history_list
                    
                    logger.info(f"📋 Combined username history: {len(username_history_list)} entries")
                    logger.info(f"📋 Combined name history: {len(name_history_list)} entries")
                
                logger.info(f"📊 Processed {processed_files} files for user {user_id}")
                logger.info(f"📊 Total unique messages: {len(merged_data['messages'])}")
                logger.info(f"📊 Total groups found: {len(merged_data['groups_info'])}")
                merged_data['total_files_merged'] = processed_files
            
            # ایجاد نام فایل نهایی
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            final_filename = f"final_{user_id}_{current_time}_{unique_id}.json"
            
            logger.info(f"✅ Merged {len(merged_data.get('messages', []))} messages for user {user_id}")
            return True, merged_data, final_filename
            
        except Exception as e:
            logger.error(f"❌ Error merging user JSON files: {e}")
            return False, None, None
    
    async def send_final_json(self, data: Dict[str, Any], filename: str) -> bool:
        """ارسال فایل JSON نهایی به Saved Messages"""
        try:
            # ایجاد فایل JSON موقت
            temp_file_path = f"temp_{filename}"
            
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # ارسال فایل به Saved Messages
            await self.client.send_document(
                chat_id=self.target_chat_id,
                document=temp_file_path,
                caption=f"📁 Final JSON for user {data.get('user_id', 'unknown')}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # حذف فایل موقت
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            logger.info(f"✅ Final JSON sent: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending final JSON: {e}")
            return False 