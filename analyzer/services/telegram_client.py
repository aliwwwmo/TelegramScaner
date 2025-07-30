import asyncio
from typing import Optional, List
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatAdminRequired, ChannelPrivate
from config.settings import TelegramConfig, MESSAGE_SETTINGS, MEMBER_SETTINGS, FILTER_SETTINGS
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
            logger.info("🔄 Initializin Telegram client...")
            
            # ایجاد کلاینت با session string
            if self.config.session_string and self.config.session_string.strip():
                logger.info("📱 Usin session string...")
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
                    logger.info("🔄 Fallin back to file-based session...")
                    self.client = Client(
                        "telegram_analyzer",
                        api_id=self.config.api_id,
                        api_hash=self.config.api_hash
                    )
            else:
                logger.info("📱No session string provided, using file-based session...")
                self.client = Client(
                    "telegram_analyzer",
                    api_id=self.config.api_id,
                    api_hash=self.config.api_hash
                )
            
            # اتصال به تلگرام
            await self.client.start()
            
            # دریافت اطلاعات کاربر
            me = await self.client.get_me()
            username = f"@{me.username}" if me.username else "No username"
            logger.info(f"✅ Successfully connected as: {me.first_name} ({username})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram client: {e}")
            raise
    
    async def get_chat_info(self, chat_link: str):
        """دریافت اطلاعات چت"""
        try:
            # استخراج username از لینک
            username = self._extract_username_from_link(chat_link)
            
            logger.info(f"🔍 Gettin info for: {username}")
            
            # بررسی لینک‌های خصوصی
            if username.startswith('joinchat/'):
                logger.info(f"🔐 Private invite link detected: {username}")
                # برای لینک‌های خصوصی، از لینک کامل استفاده کن
                chat = await self.client.get_chat(chat_link)
            else:
                # برای لینک‌های عمومی
                chat = await self.client.get_chat(username)
            
            logger.info(f"✅ Found chat: {chat.title} (ID: {chat.id}, Members: {getattr(chat, 'members_count', 'N/A')})")
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
    
    def _extract_username_from_link(self, chat_link: str) -> str:
        """استخراج username از لینک تلگرام"""
        try:
            # حذف فاصله‌ها
            chat_link = chat_link.strip()
            
            # اگر لینک شامل t.me باشد
            if 't.me/' in chat_link:
                # استخراج بخش بعد از t.me/
                parts = chat_link.split('t.me/')
                if len(parts) > 1:
                    # حذف پارامترهای URL و مسیرهای اضافی
                    username_part = parts[1].split('?')[0].split('#')[0]
                    
                    # بررسی لینک‌های خصوصی (joinchat)
                    if username_part.startswith('joinchat/'):
                        # برای لینک‌های خصوصی، کل مسیر را برگردان
                        return username_part
                    else:
                        # حذف مسیرهای اضافی (فقط بخش اول)
                        username = username_part.split('/')[0]
                        return username
            
            # اگر یوزرنیم با @ شروع شود
            elif chat_link.startswith('@'):
                return chat_link[1:]  # حذف @
            
            # اگر شماره تلفن باشد
            elif chat_link.startswith('+'):
                return chat_link
            
            # اگر لینک کامل باشد
            elif chat_link.startswith('https://') or chat_link.startswith('http://'):
                # تلاش برای استخراج از URL
                if 't.me/' in chat_link:
                    return self._extract_username_from_link(chat_link.split('t.me/')[-1])
                elif 'telegram.me/' in chat_link:
                    return self._extract_username_from_link(chat_link.split('telegram.me/')[-1])
                else:
                    return chat_link
            
            # در غیر این صورت، همان لینک را برگردان
            else:
                return chat_link
                
        except Exception as e:
            logger.error(f"❌ Error extracting username from {chat_link}: {e}")
            return chat_link
    
    async def get_chat_messages(self, chat_id, limit: int = None):
        """دریافت پیام‌های چت به صورت batch"""
        try:
            limit = limit or MESSAGE_SETTINGS.limit
            batch_size = MESSAGE_SETTINGS.batch_size
            delay = MESSAGE_SETTINGS.delay_between_batches
            
            if limit == 0:
                logger.info("📝 Message fetching disabled (limit=0)")
                return []
            
            logger.info(f"📝 Getting messages from chat {chat_id} (limit: {limit})")
            
            messages = []
            collected = 0
            
            async for message in self.client.get_chat_history(chat_id, limit=limit):
                # فیلتر کردن پیام‌های اسکن
                should_skip = False
                if message.text and FILTER_SETTINGS.filter_scan_messages:
                    text_lower = message.text.lower().strip()
                    # فیلتر کردن پیام‌های مربوط به شروع اسکن
                    if any(keyword in text_lower for keyword in FILTER_SETTINGS.scan_keywords):
                        logger.info(f"⏭️ Skipping scan start message during collection: {message.id}")
                        should_skip = True
                
                if not should_skip:
                    messages.append(message)
                    collected += 1
                    
                    # نمایش پیشرفت هر batch_size پیام
                    if collected % batch_size == 0:
                        logger.info(f"📝 Collected {collected}/{limit} messages...")
                        
                        # تاخیر بین batch ها
                        if delay > 0 and collected < limit:
                            await asyncio.sleep(delay)
                    
                    # بررسی رسیدن به حد مطلوب
                    if collected >= limit:
                        break
            
            logger.info(f"✅ Successfully collected {len(messages)} messages (filtered)")
            return messages
            
        except FloodWait as e:
            logger.warning(f"⏳ Rate limit hit, waiting {e.value} seconds...")
            await asyncio.sleep(e.value)
            return await self.get_chat_messages(chat_id, limit)
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    async def get_chat_members(self, chat_id):
        """دریافت اعضای چت"""
        members = []
        
        if not MEMBER_SETTINGS.get_members:
            logger.info("⚠️ Member fetching is disabled in settings")
            return members
        
        try:
            limit = MEMBER_SETTINGS.member_limit
            batch_size = MEMBER_SETTINGS.member_batch_size
            include_bots = MEMBER_SETTINGS.include_bots
            
            logger.info(f"👥 Getting members from chat {chat_id} (limit: {limit})...")
            
            collected = 0
            user_ids_to_save = []  # لیست user_id ها برای ذخیره در دیتابیس
            
            try:
                async for member in self.client.get_chat_members(chat_id):
                    # فیلتر کردن بات‌ها اگر نیاز باشد
                    if not include_bots and getattr(member.user, 'is_bot', False):
                        continue
                    
                    members.append(member)
                    collected += 1
                    
                    # اضافه کردن user_id به لیست برای ذخیره در دیتابیس
                    if hasattr(member.user, 'id') and member.user.id:
                        user_ids_to_save.append(member.user.id)
                    
                    # نمایش پیشرفت
                    if collected % batch_size == 0:
                        logger.info(f"👥 Collected {collected} members...")
                        await asyncio.sleep(0.5)  # تاخیر کوتاه
                    
                    # بررسی رسیدن به حد مطلوب
                    if collected >= limit:
                        break
                
                # ذخیره user_id ها در دیتابیس
                if user_ids_to_save:
                    try:
                        from services.mongo_service import MongoServiceManager
                        async with MongoServiceManager() as mongo_service:
                            saved_count = await mongo_service.save_multiple_user_ids(user_ids_to_save)
                            if saved_count > 0:
                                logger.info(f"💾 Saved {saved_count} user IDs to database")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to save users to database: {e}")
                        
            except ChatAdminRequired:
                logger.warning("⚠️ Admin access required to get member list")
            except Exception as e:
                logger.error(f"❌ Error iterating members: {e}")
            
            logger.info(f"✅ Successfully collected {len(members)} members")
            return members
            
        except FloodWait as e:
            logger.warning(f"⏳ Rate limit hit for members, waiting {e.value} seconds...")
            await asyncio.sleep(e.value)
            return await self.get_chat_members(chat_id)
        except Exception as e:
            logger.error(f"❌ Error getting chat members: {e}")
            return members
    
    async def get_chat_members_basic(self, chat_id, limit: int = 1000):
        """دریافت اعضای چت به روش پایه (برای چت‌هایی که دسترسی کامل ندارند)"""
        try:
            logger.info(f"👥 Getting basic member info from chat {chat_id}...")
            
            members = []
            user_ids = set()  # برای جلوگیری از تکرار
            user_ids_to_save = []  # لیست user_id ها برای ذخیره در دیتابیس
            
            # دریافت کاربران از پیام‌های اخیر
            async for message in self.client.get_chat_history(chat_id, limit=limit):
                if message.from_user and message.from_user.id not in user_ids:
                    members.append(message.from_user)
                    user_ids.add(message.from_user.id)
                    user_ids_to_save.append(message.from_user.id)
                    
                    if len(members) % 50 == 0:
                        logger.info(f"👥 Found {len(members)} unique users from messages...")
            
            # ذخیره user_id ها در دیتابیس
            if user_ids_to_save:
                try:
                    from services.mongo_service import MongoServiceManager
                    async with MongoServiceManager() as mongo_service:
                        saved_count = await mongo_service.save_multiple_user_ids(user_ids_to_save)
                        if saved_count > 0:
                            logger.info(f"💾 Saved {saved_count} user IDs from messages to database")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save users from messages to database: {e}")
            
            logger.info(f"✅ Found {len(members)} unique users from recent messages")
            return members
            
        except Exception as e:
            logger.error(f"❌ Error getting basic member info: {e}")
            return []
    
    async def analyze_chat_complete(self, chat_link: str):
        """تحلیل کامل چت (پیام‌ها + اعضا)"""
        try:
            # دریافت اطلاعات چت
            chat = await self.get_chat_info(chat_link)
            if not chat:
                return None, [], []
            
            # دریافت پیام‌ها
            messages = await self.get_chat_messages(chat.id)
            
            # دریافت اعضا
            members = []
            if MEMBER_SETTINGS.get_members:
                try:
                    # ابتدا سعی کنید لیست کامل اعضا را دریافت کنید
                    members = await self.get_chat_members(chat.id)
                except:
                    # اگر نتوانستید، از پیام‌ها اطلاعات کاربران را استخراج کنید
                    logger.info("� Falling back to extracting users from messages...")
                    members = await self.get_chat_members_basic(chat.id, MESSAGE_SETTINGS.limit)
            
            return chat, messages, members
            
        except Exception as e:
            logger.error(f"❌ Error in complete chat analysis: {e}")
            return None, [], []
    
    async def close(self):
        """بستن کلاینت"""
        if self.client:
            try:
                await self.client.stop()
                logger.info("🔌Telegram client disconnected")
            except Exception as e:
                logger.error(f"❌ Error closing client: {e}")
