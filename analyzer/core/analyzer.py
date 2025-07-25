import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from services.telegram_client import TelegramClientManager
from config.settings import TelegramConfig, AnalysisConfig
from utils.logger import logger

class TelegramAnalyzer:
    """کلاس اصلی تحلیل تلگرام"""
    
    def __init__(self, telegram_config: TelegramConfig, analysis_config: AnalysisConfig):
        self.telegram_config = telegram_config
        self.analysis_config = analysis_config
        self.results = []
    
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
                    
                    # تحلیل داده‌ها
                    analysis_result = self.analyze_chat_data(chat_info, messages)
                    self.results.append(analysis_result)
                    
                    logger.info(f"✅ Completed analysis for {chat_info.title}")
                    
                    # توقف کوتاه بین درخواست‌ها
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error analyzing {chat_link}: {e}")
                    continue
        
        # ذخیره نتایج
        await self.save_results()
        
        if self.results:
            logger.info(f"🎉 Analysis completed! {len(self.results)} chats analyzed successfully.")
        else:
            logger.warning("⚠️ No chats were successfully analyzed.")
    
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
                            'message_count': 0
                        }
                    users[user_id]['message_count'] += 1
            
            # مرتب‌سازی کاربران بر اساس تعداد پیام
            top_users = sorted(users.values(), key=lambda x: x['message_count'], reverse=True)[:10]
            
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
                    'analysis_date': datetime.now().isoformat()
                },
                'top_users': top_users,
                'sample_messages': [
                    {
                        'id': msg.id,
                        'date': msg.date.isoformat() if msg.date else None,
                        'text': msg.text[:100] if msg.text else None,
                        'user': {
                            'id': msg.from_user.id if msg.from_user else None,
                            'first_name': msg.from_user.first_name if msg.from_user else None
                        }
                    }
                    for msg in messages[:5]  # فقط 5 پیام نمونه
                ]
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
            
            logger.info(f"💾 Results saved to: {output_path}")
            
            # خلاصه نتایج
            total_chats = len(self.results)
            total_messages = sum(r['statistics']['total_messages'] for r in self.results)
            total_users = sum(r['statistics']['total_users'] for r in self.results)
            
            logger.info(f"📊 Summary: {total_chats} chats, {total_messages} messages, {total_users} unique users")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
