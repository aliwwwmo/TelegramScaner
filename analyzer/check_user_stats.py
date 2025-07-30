#!/usr/bin/env python3
"""
Script to check user statistics and demonstrate user storage functionality
"""

import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from services.mongo_service import MongoServiceManager
from utils.logger import logger

async def check_user_statistics():
    """بررسی آمار کاربران"""
    logger.info("📊 Checking user statistics...")
    
    try:
        async with MongoServiceManager() as mongo_service:
            # دریافت تعداد کل کاربران
            total_users = await mongo_service.get_user_count()
            logger.info(f"👥 Total users in database: {total_users:,}")
            
            # دریافت آمار کاربران
            user_stats = await mongo_service.get_user_stats()
            logger.info("📈 User Statistics:")
            logger.info(f"   ├── Total users: {user_stats.get('total_users', 0):,}")
            logger.info(f"   ├── New users today: {user_stats.get('today_new_users', 0):,}")
            logger.info(f"   └── New users this week: {user_stats.get('week_new_users', 0):,}")
            
            # دریافت کاربران اخیر
            recent_users = await mongo_service.get_recent_users(hours=24)
            logger.info(f"🕐 Recent users (last 24h): {len(recent_users):,}")
            
            if recent_users:
                logger.info(f"   └── Sample recent user IDs: {recent_users[:5]}")
            
            # نمایش نمونه‌ای از کاربران اخیر
            if recent_users:
                logger.info("📋 Sample of recent user IDs:")
                for i, user_id in enumerate(recent_users[:10]):
                    logger.info(f"   {i+1:2d}. {user_id}")
                if len(recent_users) > 10:
                    logger.info(f"   ... and {len(recent_users) - 10} more")
            
            logger.info("✅ User statistics check completed!")
            
    except Exception as e:
        logger.error(f"❌ Failed to check user statistics: {e}")

async def main():
    """تابع اصلی"""
    logger.info("🚀 Starting user statistics check...")
    await check_user_statistics()

if __name__ == "__main__":
    asyncio.run(main()) 