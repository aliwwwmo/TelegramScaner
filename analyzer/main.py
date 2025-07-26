import asyncio
import sys
import os
from pathlib import Path

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import TELEGRAM_CONFIG, ANALYSIS_CONFIG, MESSAGE_SETTINGS, MEMBER_SETTINGS
from services.telegram_client import TelegramClientManager
from services.user_tracker import UserTracker
from services.chat_analyzer import ChatAnalyzer
from services.message_analyzer import MessageAnalyzer
from services.link_analyzer import LinkAnalyzer
from utils.logger import logger

async def analyze_single_chat(chat_link: str):
    """تحلیل یک چت"""
    logger.info(f"🔍 Starting analysis for: {chat_link}")
    
    async with TelegramClientManager(TELEGRAM_CONFIG) as client:
        # تحلیل کامل چت
        chat, messages, members = await client.analyze_chat_complete(chat_link)
        
        if not chat:
            logger.error(f"❌ Could not access chat: {chat_link}")
            return None
        
        # آماده سازی tracker و analyzer
        user_tracker = UserTracker()
        link_analyzer = LinkAnalyzer()
        message_analyzer = MessageAnalyzer(client.client, link_analyzer)
        
        # اطلاعات چت
        chat_info = {
            'id': chat.id,
            'title': chat.title,
            'username': getattr(chat, 'username', None),
            'type': str(chat.type),
            'members_count': getattr(chat, 'members_count', 0),
            'description': getattr(chat, 'description', ''),
            'link': chat_link
        }
        
        logger.info(f"📊 Chat Info: {chat_info['title']} ({chat_info['members_count']} members)")
        
        # پردازش پیام‌ها
        if messages:
            logger.info(f"📝 Processing {len(messages)} messages...")
            for message in messages:
                user_tracker.process_message(message, chat_info)
                # همچنین با message_analyzer پردازش کنیم
                await message_analyzer.process_user_message(message, str(chat.id), chat.title)
            
            # تحلیل پیام‌ها - ایجاد یک تحلیل ساده
            analysis_results = {
                'total_messages': len(messages),
                'messages': [],
                'users_analyzed': len(message_analyzer.processed_users)
            }
        else:
            logger.info("📝 No messages to process")
            analysis_results = {}
        
        # پردازش اعضا (اگر دریافت شده باشند)
        if members:
            logger.info(f"👥 Processing {len(members)} members...")
            if hasattr(members[0], 'user'):  # اگر ChatMember objects هستند
                for member in members:
                    user_tracker.add_user_from_member(member, chat_info)
            else:  # اگر User objects هستند
                for user in members:
                    user_tracker.add_user_direct(user, chat_info)
        
        # ذخیره نتایج
        results_file = Path(ANALYSIS_CONFIG.results_dir) / ANALYSIS_CONFIG.output_file
        # اطمینان از وجود پوشه والد
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ذخیره کاربران
        users_saved = user_tracker.save_all_users()
        
        # آمار نهایی
        stats = user_tracker.get_stats()
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   💬 Messages processed: {len(messages)}")
        logger.info(f"   👥 Members found: {len(members)}")
        logger.info(f"   👤 Unique users: {stats['total_users']}")
        logger.info(f"   🤖 Bots: {stats['bot_users']}")
        logger.info(f"   ❌ Deleted: {stats['deleted_users']}")
        logger.info(f"   ✅ Active: {stats['active_users']}")
        logger.info(f"   💾 Users saved: {users_saved}")
        
        return {
            'chat_info': chat_info,
            'stats': stats,
            'analysis': analysis_results,
            'users_saved': users_saved
        }

async def main():
    """تابع اصلی"""
    try:
        logger.info("🚀 Starting Telegram Chat Analyzer...")
        logger.info(f"📝 Settings:")
        logger.info(f"   📝 Message limit: {MESSAGE_SETTINGS.limit}")
        logger.info(f"   👥 Get members: {MEMBER_SETTINGS.get_members}")
        logger.info(f"   👥 Member limit: {MEMBER_SETTINGS.member_limit}")
        
        # خواندن لینک‌ها از فایل
        links_file = Path(ANALYSIS_CONFIG.links_file)
        if not links_file.exists():
            logger.error(f"❌ Links file not found: {links_file}")
            return
        
        with open(links_file, 'r', encoding='utf-8') as f:
            chat_links = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not chat_links:
            logger.error("❌ No chat links found in file")
            return
        
        logger.info(f"📋 Found {len(chat_links)} chat(s) to analyze")
        
        # تحلیل هر چت
        all_results = []
        for i, chat_link in enumerate(chat_links, 1):
            logger.info(f"🔍 Analyzing chat {i}/{len(chat_links)}: {chat_link}")
            
            result = await analyze_single_chat(chat_link)
            if result:
                all_results.append(result)
                logger.info(f"✅ Chat {i} completed successfully")
            else:
                logger.error(f"❌ Chat {i} failed")
            
            # تاخیر بین چت‌ها
            if i < len(chat_links):
                await asyncio.sleep(2)
        
        # ذخیره نتایج کلی
        if all_results:
            import json
            results_file = Path(ANALYSIS_CONFIG.results_dir) / ANALYSIS_CONFIG.output_file
            # اطمینان از وجود پوشه والد
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            summary = {
                'total_chats': len(all_results),
                'total_messages': sum(len(r.get('analysis', {}).get('messages', [])) for r in all_results),
                'total_users': sum(r['stats']['total_users'] for r in all_results),
                'results': all_results,
                'settings': {
                    'message_limit': MESSAGE_SETTINGS.limit,
                    'member_limit': MEMBER_SETTINGS.member_limit,
                    'get_members': MEMBER_SETTINGS.get_members
                }
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 Results saved to: {results_file}")
            logger.info(f"✅ Analysis completed! Processed {len(all_results)} chats")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Analysis stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
