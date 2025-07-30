#!/usr/bin/env python3
"""
Test script for user storage functionality
"""

import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from services.mongo_service import MongoServiceManager
from utils.logger import logger

async def test_user_storage():
    """تست عملکرد ذخیره کاربران"""
    logger.info("🧪 Testing user storage functionality...")
    
    try:
        async with MongoServiceManager() as mongo_service:
            # تست ذخیره یک کاربر
            test_user_id = 123456789
            success = await mongo_service.save_user_id(test_user_id)
            if success:
                logger.info(f"✅ Successfully saved user {test_user_id}")
            else:
                logger.error(f"❌ Failed to save user {test_user_id}")
            
            # تست ذخیره چندین کاربر
            test_user_ids = [111111111, 222222222, 333333333, 444444444, 555555555]
            saved_count = await mongo_service.save_multiple_user_ids(test_user_ids)
            logger.info(f"✅ Saved {saved_count} users in batch")
            
            # تست دریافت تعداد کاربران
            user_count = await mongo_service.get_user_count()
            logger.info(f"📊 Total users in database: {user_count}")
            
            # تست دریافت آمار کاربران
            user_stats = await mongo_service.get_user_stats()
            logger.info(f"📈 User statistics: {user_stats}")
            
            # تست دریافت کاربران اخیر
            recent_users = await mongo_service.get_recent_users(hours=24)
            logger.info(f"🕐 Recent users (last 24h): {len(recent_users)}")
            
            logger.info("🎉 User storage test completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

async def main():
    """تابع اصلی"""
    logger.info("🚀 Starting user storage test...")
    await test_user_storage()

if __name__ == "__main__":
    asyncio.run(main()) 