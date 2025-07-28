#!/usr/bin/env python3
"""
تست یکپارچگی MongoDB
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import MONGO_CONFIG
from services.mongo_service import MongoServiceManager
from models.data_models import GroupInfo, ChatType, ScanStatus
from utils.logger import logger

async def test_mongo_connection():
    """تست اتصال به MongoDB"""
    print("🔧 Testing MongoDB connection...")
    
    async with MongoServiceManager() as mongo_service:
        # تست ذخیره یک گروه نمونه
        test_group = GroupInfo(
            chat_id=123456789,
            username="test_group",
            link="https://t.me/test_group",
            chat_type=ChatType.GROUP,
            is_public=True
        )
        
        # ذخیره گروه
        success = await mongo_service.save_group_info(test_group)
        if success:
            print("✅ Test group saved successfully")
        else:
            print("❌ Failed to save test group")
            return False
        
        # بازیابی گروه
        retrieved_group = await mongo_service.get_group_info(123456789)
        if retrieved_group:
            print("✅ Test group retrieved successfully")
            print(f"   Username: @{retrieved_group.username}")
            print(f"   Type: {retrieved_group.chat_type.value}")
            print(f"   Public: {retrieved_group.is_public}")
        else:
            print("❌ Failed to retrieve test group")
            return False
        
        # تست آمار
        stats = await mongo_service.get_stats()
        if stats:
            print("✅ Statistics retrieved successfully")
            print(f"   Total groups: {stats.get('total_groups', 0)}")
        else:
            print("❌ Failed to retrieve statistics")
            return False
        
        # حذف گروه تست
        deleted = await mongo_service.delete_group(123456789)
        if deleted:
            print("✅ Test group deleted successfully")
        else:
            print("❌ Failed to delete test group")
        
        return True

async def test_mongo_operations():
    """تست عملیات مختلف MongoDB"""
    print("\n🔧 Testing MongoDB operations...")
    
    async with MongoServiceManager() as mongo_service:
        # ایجاد چندین گروه تست
        test_groups = [
            GroupInfo(
                chat_id=111111111,
                username="channel1",
                link="https://t.me/channel1",
                chat_type=ChatType.CHANNEL,
                is_public=True
            ),
            GroupInfo(
                chat_id=222222222,
                username=None,
                link="https://t.me/joinchat/abc123",
                chat_type=ChatType.GROUP,
                is_public=False
            ),
            GroupInfo(
                chat_id=333333333,
                username="supergroup",
                link="https://t.me/supergroup",
                chat_type=ChatType.SUPERGROUP,
                is_public=True
            )
        ]
        
        # ذخیره گروه‌ها
        for group in test_groups:
            success = await mongo_service.save_group_info(group)
            if success:
                print(f"✅ Saved: {group.chat_id}")
            else:
                print(f"❌ Failed to save: {group.chat_id}")
        
        # تست جستجو بر اساس username
        group = await mongo_service.get_group_by_username("channel1")
        if group:
            print(f"✅ Found group by username: {group.chat_id}")
        
        # تست گروه‌های عمومی
        public_groups = await mongo_service.get_groups_by_status(ScanStatus.SUCCESS)
        print(f"✅ Found {len(public_groups)} groups with successful scans")
        
        # تست اسکن‌های اخیر
        recent_groups = await mongo_service.get_recent_scans(24)
        print(f"✅ Found {len(recent_groups)} groups scanned in last 24 hours")
        
        # حذف گروه‌های تست
        for group in test_groups:
            await mongo_service.delete_group(group.chat_id)
            print(f"✅ Deleted: {group.chat_id}")

async def main():
    """تابع اصلی تست"""
    print("🚀 Starting MongoDB integration tests...")
    
    try:
        # تست اتصال
        connection_success = await test_mongo_connection()
        if not connection_success:
            print("❌ MongoDB connection test failed")
            return
        
        # تست عملیات
        await test_mongo_operations()
        
        print("\n✅ All MongoDB tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 