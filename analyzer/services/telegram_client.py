import asyncio
from typing import Optional, List
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatAdminRequired, ChannelPrivate
from config.settings import TelegramConfig
from utils.logger import logger

class TelegramClientManager:
    """مدیریت کلاینت تلگرام"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.client: Optional[Client] = None
    
    async def __aenter__(self):
        """ورود به async context manager"""
        await self.initialize_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """خروج از async context manager"""
        await self.close()
    
    async def initialize_client(self) -> bool:
        """راه‌اندازی کلاینت تلگرام"""
        try:
            logger.info("🔄 Initializing Telegram client...")
            
            # ایجاد کلاینت با session string
            if self.config.session_string and self.config.session_string.strip():
                logger.info("📱 Using session string...")
                try:
                    self.client = Client(
                        "telegram_analyzer",
                        api_id=self.config.api_id,
                        api_hash=self.config.api_hash,
                        session_string=self.config.session_string,
                        in_memory=True  # این خط مهم است
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to create client with session string: {e}")
                    logger.info("🔄 Falling back to file-based session...")
                    self.client = Client(
                        "telegram_analyzer",
                        api_id=self.config.api_id,
                        api_hash=self.config.api_hash
                    )
            else:
                logger.info("📱 No session string provided, using file-based session...")
                self.client = Client(
                    "telegram_analyzer",
                    api_id=self.config.api_id,
                    api_hash=self.config.api_hash
                )
            
            # اتصال به تلگرام
            await self.client.start()
            
            # دریافت اطلاعات کاربر
            me = await self.client.get_me()
            logger.info(f"✅ Successfully connected as: {me.first_name} (@{me.username})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram client: {e}")
            raise
    
    async def get_chat_info(self, chat_link: str):
        """دریافت اطلاعات چت"""
        try:
            # استخراج username از لینک
            if 't.me/' in chat_link:
                username = chat_link.split('t.me/')[-1].split('?')[0].split('/')[0]
            elif '@' in chat_link:
                username = chat_link.replace('@', '')
            else:
                username = chat_link
            
            # حذف کاراکترهای اضافی
            username = username.strip().replace('+', '')
            
            logger.info(f"🔍 Getting info for: {username}")
            
            # دریافت اطلاعات چت
            chat = await self.client.get_chat(username)
            return chat
            
        except ChannelPrivate:
            logger.error(f"❌ Private channel: {chat_link}")
            return None
        except FloodWait as e:
            logger.warning(f"⏳ Rate limit hit, waiting {e.value} seconds...")
            await asyncio.sleep(e.value)
            return await self.get_chat_info(chat_link)
        except Exception as e:
            logger.error(f"❌ Error getting chat info for {chat_link}: {e}")
            return None
    
    async def get_chat_messages(self, chat_id, limit: int = 100):
        """دریافت پیام‌های چت"""
        try:
            messages = []
            async for message in self.client.get_chat_history(chat_id, limit=limit):
                messages.append(message)
            return messages
            
        except FloodWait as e:
            logger.warning(f"⏳ Rate limit hit, waiting {e.value} seconds...")
            await asyncio.sleep(e.value)
            return await self.get_chat_messages(chat_id, limit)
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    async def close(self):
        """بستن کلاینت"""
        if self.client:
            try:
                await self.client.stop()
                logger.info("🔌 Telegram client disconnected")
            except Exception as e:
                logger.error(f"❌ Error closing client: {e}")
