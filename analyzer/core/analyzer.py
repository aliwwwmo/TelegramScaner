import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from services.telegram_client import TelegramClientManager
from services.user_tracker import UserTracker
from config.settings import TelegramConfig, AnalysisConfig
from utils.logger import logger

class TelegramAnalyzer:
    """کلاس اصلی تحلیل تلگرام"""
    
    def __init__(self, telegram_config: TelegramConfig, analysis_config: AnalysisConfig):
        self.telegram_config = telegram_config
        self.analysis_config = analysis_config
        self.results = []
        self.user_tracker = UserTracker()
    
    async def run_analysis(self, chat_links: List[str]):
        """اجرای تحلیل روی لیست چت‌ها"""
        logger.info(f"🚀 Starting analysis of {len(chat_links)} chats...")
        
        async with TelegramClientManager(self.telegram_config) as client:
            for i, chat_link in enumerate(chat_links, 1):
                logger.info(f"📊 Analyzing chat {i}/{len(chat_links)}: {chat_link}")
                
                try:
                    # دریافت اطلاعات چت
                    chat_info = await client.get_chat_info(chat_link)
                    if not chat_info:
                        logger.warning(f"⚠️ Could not get info for: {chat_link}")
                        continue
                    
                    logger.info(f"✅ Found chat: {chat_info.title} (ID: {chat_info.id})")
                    
                    # دریافت پیام‌ها
                    logger.info(f"📥 Getting messages...")
                    messages = await client.get_chat_messages(
                        chat_info.id, 
                        limit=self.analysis_config.messages_per_chat
                    )
                    
                    logger.info(f"📥 Retrieved {len(messages)} messages")
                    
                    # پردازش پیام‌ها برای ردیابی کاربران
                    logger.info(f"👥 Processing users from messages...")
                    await self.process_messages_for_users(messages, chat_info)
                    
                    # تحلیل داده‌های چت
                    analysis_result = self.analyze_chat_data(chat_info, messages)
                    self.results.append(analysis_result)
                    
                    logger.info(f"✅ Completed analysis for {chat_info.title}")
                    
                    # توقف کوتاه بین درخواست‌ها
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error analyzing {chat_link}: {e}")
                    continue
        
        # ذخیره نتایج چت‌ها
        await self.save_results()
        
        # ذخیره اطلاعات کاربران
        logger.info("💾 Saving user profiles...")
        self.user_tracker.save_all_users()
        
        # نمایش آمار
        await self.show_final_statistics()
        
        if self.results:
            logger.info(f"🎉 Analysis completed! {len(self.results)} chats analyzed successfully.")
        else:
            logger.warning("⚠️ No chats were successfully analyzed.")
    
    async def process_messages_for_users(self, messages, chat_info):
        """پردازش پیام‌ها برای ردیابی کاربران"""
        processed_users = set()
        
        for message in messages:
            if message.from_user and message.from_user.id not in processed_users:
                processed_users.add(message.from_user.id)
            
            # پردازش پیام توسط user_tracker
            self.user_tracker.process_message(message, chat_info)
        
        logger.info(f"👥 Processed {len(processed_users)} unique users from {len(messages)} messages")
    
    def analyze_chat_data(self, chat_info, messages) -> Dict[str, Any]:
        """تحلیل داده‌های چت"""
        try:
            # آمار پایه
            total_messages = len(messages)
            
            # تحلیل کاربران
            users = {}
            for message in messages:
                if message.from_user:
                    user_id = message.from_user.id
                    if user_id not in users:
                        users[user_id] = {
                            'id': user_id,
                            'first_name': message.from_user.first_name,
                            'last_name': message.from_user.last_name,
                            'username': message.from_user.username,
                            'message_count': 0,
                            'is_bot': getattr(message.from_user, 'is_bot', False)
                        }
                    users[user_id]['message_count'] += 1
            
            # مرتب‌سازی کاربران بر اساس تعداد پیام
            top_users = sorted(users.values(), key=lambda x: x['message_count'], reverse=True)[:10]
            
            # آمار انواع پیام
            message_types = {
                'text': 0,
                'photo': 0,
                'video': 0,
                'audio': 0,
                'document': 0,
                'sticker': 0,
                'voice': 0,
                'other': 0
            }
            
            for message in messages:
                if message.text:
                    message_types['text'] += 1
                elif message.photo:
                    message_types['photo'] += 1
                elif message.video:
                    message_types['video'] += 1
                elif message.audio:
                    message_types['audio'] += 1
                elif message.document:
                    message_types['document'] += 1
                elif message.sticker:
                    message_types['sticker'] += 1
                elif message.voice:
                    message_types['voice'] += 1
                else:
                    message_types['other'] += 1
            
            return {
                'chat_info': {
                    'id': chat_info.id,
                    'title': chat_info.title,
                    'type': str(chat_info.type),
                    'members_count': getattr(chat_info, 'members_count', 0),
                    'username': chat_info.username,
                    'description': getattr(chat_info, 'description', '')
                },
                'statistics': {
                    'total_messages': total_messages,
                    'total_users': len(users),
                    'bot_users': sum(1 for u in users.values() if u.get('is_bot', False)),
                    'analysis_date': datetime.now().isoformat(),
                    'message_types': message_types
                },
                'top_users': top_users
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing chat data: {e}")
            return {
                'chat_info': {'title': 'Unknown', 'error': str(e)},
                'statistics': {'total_messages': 0, 'error': str(e)}
            }
    
    async def save_results(self):
        """ذخیره نتایج در فایل"""
        try:
            if not self.results:
                logger.warning("⚠️ No results to save")
                return
            
            # ایجاد دایرکتوری نتایج
            os.makedirs(self.analysis_config.results_dir, exist_ok=True)
            
            # مسیر فایل خروجی
            output_path = os.path.join(
                self.analysis_config.results_dir, 
                self.analysis_config.output_file
            )
            
            # ذخیره در فایل JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Chat analysis results saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
    
    async def show_final_statistics(self):
        """نمایش آمار نهایی"""
        try:
            # آمار چت‌ها
            total_chats = len(self.results)
            total_messages = sum(r['statistics']['total_messages'] for r in self.results)
            
            # آمار کاربران
            user_stats = self.user_tracker.get_statistics()
            
            logger.info("📊 ===== FINAL STATISTICS =====")
            logger.info(f"📱 Analyzed Chats: {total_chats}")
            logger.info(f"💬 Total Messages: {total_messages}")
            logger.info(f"👥 Total Users: {user_stats['total_users']}")
            logger.info(f"🤖 Bot Users: {user_stats['bot_users']}")
            logger.info(f"🗑️ Deleted Users: {user_stats['deleted_users']}")
            logger.info(f"✅ Active Users: {user_stats['active_users']}")
            logger.info(f"📁 User files saved in: users/")
            logger.info("================================")
            
        except Exception as e:
            logger.error(f"❌ Error showing statistics: {e}")
