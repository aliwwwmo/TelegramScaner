import json
import os
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from config.settings import TELEGRAM_CONFIG
from config.telegram_storage_config import TelegramStorageConfig
from utils.logger import logger

class TelegramStorage:
    """ارسال فایل‌های JSON به تلگرام به عنوان کلاود استوریج"""
    
    def __init__(self, target_chat_id: int = None):
        # اگر target_chat_id تنظیم نشده، از تنظیمات استفاده کن
        if target_chat_id is None:
            target_chat_id = TelegramStorageConfig.get_target_chat_id()
        
        self.target_chat_id = target_chat_id
        self.api_id = TELEGRAM_CONFIG.api_id
        self.api_hash = TELEGRAM_CONFIG.api_hash
        self.session_string = TELEGRAM_CONFIG.session_string
        self.client = None
        
    async def __aenter__(self):
        """شروع کلاینت تلگرام"""
        try:
            self.client = Client(
                "telegram_storage",
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_string=self.session_string
            )
            await self.client.start()
            
            # اگر target_chat_id تنظیم نشده، از Saved Messages استفاده کن
            if self.target_chat_id is None or TelegramStorageConfig.should_use_saved_messages():
                me = await self.client.get_me()
                self.target_chat_id = me.id
                logger.info(f"✅ Using Saved Messages (ID: {self.target_chat_id})")
            else:
                logger.info(f"✅ Using target chat (ID: {self.target_chat_id})")
            
            logger.info("✅ Telegram storage client started")
            return self
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram storage client: {e}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """توقف کلاینت تلگرام"""
        if self.client:
            await self.client.stop()
            logger.info("🛑 Telegram storage client stopped")
    
    async def send_json_file(self, data: Dict[str, Any], filename: str, caption: str = None) -> bool:
        """ارسال فایل JSON به تلگرام"""
        try:
            if not self.client:
                logger.error("❌ Telegram client not initialized")
                return False
            
            # تست اتصال به چت
            try:
                chat = await self.client.get_chat(self.target_chat_id)
                logger.debug(f"✅ Connected to chat: {chat.title or chat.id}")
            except Exception as e:
                logger.error(f"❌ Cannot access target chat {self.target_chat_id}: {e}")
                return False
            
            # ایجاد فایل JSON موقت
            temp_file_path = f"temp_{filename}"
            
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # ارسال فایل به تلگرام
            try:
                await self.client.send_document(
                    chat_id=self.target_chat_id,
                    document=temp_file_path,
                    caption=caption or f"📁 {filename}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                logger.info(f"✅ File sent to Telegram: {filename}")
                return True
                
            except FloodWait as e:
                logger.warning(f"⚠️ Flood wait: {e.value} seconds")
                await asyncio.sleep(e.value)
                return await self.send_json_file(data, filename, caption)
                
            except RPCError as e:
                logger.error(f"❌ RPC Error sending file: {e}")
                return False
                
            finally:
                # حذف فایل موقت
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
        except Exception as e:
            logger.error(f"❌ Error sending JSON file: {e}")
            return False
    
    async def send_user_data(self, user_data: Dict[str, Any], user_id: int, group_info: Dict[str, Any]) -> bool:
        """ارسال داده‌های کاربر به تلگرام"""
        try:
            # ایجاد نام فایل مناسب با فرمت جدید
            group_id = group_info.get('group_id', 'unknown')
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]  # 8 کاراکتر اول UUID
            
            filename = f"{user_id}_{group_id}_{current_time}_{unique_id}.json"
            
            # ایجاد caption مناسب
            user_name = user_data.get('current_name', 'Unknown')
            username = user_data.get('current_username', '')
            message_count = len(user_data.get('messages_in_this_group', []))
            
            caption = f"👤 User: {user_name}"
            if username:
                caption += f" (@{username})"
            caption += f"\n📊 Messages: {message_count}"
            caption += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return await self.send_json_file(user_data, filename, caption)
            
        except Exception as e:
            logger.error(f"❌ Error sending user data: {e}")
            return False
    
    async def send_summary_file(self, summary_data: Dict[str, Any]) -> bool:
        """ارسال فایل خلاصه به تلگرام"""
        try:
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]  # 8 کاراکتر اول UUID
            filename = f"summary_{current_time}_{unique_id}.json"
            
            caption = f"📊 Analysis Summary"
            caption += f"\n👥 Total Users: {summary_data.get('summary', {}).get('total_users', 0)}"
            caption += f"\n📝 Total Files: {summary_data.get('summary', {}).get('total_files_created', 0)}"
            caption += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return await self.send_json_file(summary_data, filename, caption)
            
        except Exception as e:
            logger.error(f"❌ Error sending summary file: {e}")
            return False 