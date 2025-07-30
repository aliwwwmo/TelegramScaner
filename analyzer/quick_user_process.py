#!/usr/bin/env python3
"""
اسکریپت سریع برای پردازش فایل‌های JSON کاربران
"""

import asyncio
import sys
import os
from pathlib import Path

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from user_json_processor import UserJSONProcessor
from utils.logger import logger

async def quick_process_user(user_id: int):
    """پردازش سریع یک کاربر"""
    try:
        logger.info(f"🚀 Quick processing user {user_id}...")
        
        processor = UserJSONProcessor()
        success = await processor.process_user_json(user_id)
        
        if success:
            logger.info(f"✅ User {user_id} processed successfully!")
            return True
        else:
            logger.error(f"❌ Failed to process user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error processing user {user_id}: {e}")
        return False

async def main():
    """تابع اصلی"""
    if len(sys.argv) != 2:
        print("Usage: python quick_user_process.py <user_id>")
        print("Example: python quick_user_process.py 123456789")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("❌ Invalid user_id. Please provide a valid number.")
        sys.exit(1)
    
    success = await quick_process_user(user_id)
    
    if success:
        print(f"🎉 User {user_id} processed successfully!")
        sys.exit(0)
    else:
        print(f"❌ Failed to process user {user_id}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 