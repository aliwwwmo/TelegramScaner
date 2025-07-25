import asyncio
import sys
import os
from dotenv import load_dotenv

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

from config.settings import TelegramConfig, AnalysisConfig
from core.analyzer import TelegramAnalyzer
from services.file_manager import FileManager
from utils.logger import logger

async def main():
    """تابع اصلی"""
    try:
        # نمایش متغیرهای محیطی برای دیباگ
        logger.info("🔍 Checking environment variables...")
        api_id = os.getenv('API_ID')
        api_hash = os.getenv('API_HASH')
        
        if not api_id:
            logger.error("❌ API_ID not found in .env file")
            logger.info("📝 Please create .env file with your Telegram API credentials")
            return
        
        if not api_hash:
            logger.error("❌ API_HASH not found in .env file")
            logger.info("📝 Please add API_HASH to your .env file")
            return
        
        logger.info(f"✅ API_ID found: {api_id}")
        logger.info(f"✅ API_HASH found: {api_hash[:10]}...")
        
        # بارگذاری تنظیمات
        telegram_config = TelegramConfig.from_env()
        analysis_config = AnalysisConfig.from_env()
        
        # ایجاد مدیر فایل و بارگذاری لینک‌ها
        file_manager = FileManager(analysis_config)
        chat_links = file_manager.load_links_from_file()
        
        if not chat_links:
            return
        
        # ایجاد analyzer و اجرای تحلیل
        analyzer = TelegramAnalyzer(telegram_config, analysis_config)
        await analyzer.run_analysis(chat_links)
        
    except ValueError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info("⏹️ Analysis interrupted by user")
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")

def run():
    """اجرای برنامه"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Program interrupted by user")
    except Exception as e:
        logger.error(f"❌ Program failed: {e}")

if __name__ == "__main__":
    run()
