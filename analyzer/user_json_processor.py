import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from services.user_json_manager import UserJSONManager
from services.mongo_service import MongoServiceManager
from utils.logger import logger

class UserJSONProcessor:
    """پردازشگر فایل‌های JSON کاربران"""
    
    def __init__(self):
        self.user_json_manager = None
        self.mongo_service = None
    
    async def process_user_json(self, user_id: int) -> bool:
        """پردازش فایل‌های JSON یک کاربر"""
        try:
            logger.info(f"🔍 Starting JSON processing for user {user_id}")
            
            # بررسی اینکه آیا فایل نهایی قبلاً در دیتابیس ثبت شده
            async with MongoServiceManager() as mongo_service:
                existing_filename = await mongo_service.get_user_final_json_filename(user_id)
                
                if existing_filename:
                    logger.info(f"📋 Found existing final JSON filename for user {user_id}: {existing_filename}")
                
                # ترکیب فایل‌های JSON
                async with UserJSONManager() as json_manager:
                    success, merged_data, final_filename = await json_manager.merge_user_json_files(user_id)
                    
                    if not success:
                        logger.error(f"❌ Failed to merge JSON files for user {user_id}")
                        return False
                    
                    if not merged_data:
                        logger.warning(f"⚠️ No data to merge for user {user_id}")
                        return False
                    
                    # ارسال فایل نهایی به Saved Messages
                    sent = await json_manager.send_final_json(merged_data, final_filename)
                    
                    if not sent:
                        logger.error(f"❌ Failed to send final JSON for user {user_id}")
                        return False
                    
                    # ذخیره نام فایل نهایی در دیتابیس
                    message_count = len(merged_data.get('messages', []))
                    saved = await mongo_service.update_user_final_json_info(
                        user_id, final_filename, message_count
                    )
                    
                    if not saved:
                        logger.warning(f"⚠️ Failed to save final JSON filename to database for user {user_id}")
                    
                    logger.info(f"✅ Successfully processed user {user_id}")
                    logger.info(f"📊 Final JSON: {final_filename}")
                    logger.info(f"📝 Total messages: {message_count}")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error processing user {user_id}: {e}")
            return False
    
    async def get_user_info(self, user_id: int) -> Optional[dict]:
        """دریافت اطلاعات کاربر از دیتابیس"""
        try:
            async with MongoServiceManager() as mongo_service:
                user_data = mongo_service.users_collection.find_one({"user_id": user_id})
                return user_data
        except Exception as e:
            logger.error(f"❌ Error getting user info for {user_id}: {e}")
            return None
    
    async def list_processed_users(self) -> list:
        """لیست کاربرانی که فایل نهایی دارند"""
        try:
            async with MongoServiceManager() as mongo_service:
                cursor = mongo_service.users_collection.find({
                    "final_json_filename": {"$exists": True}
                }).sort("final_json_updated", -1)
                
                users = []
                for user in cursor:
                    users.append({
                        "user_id": user["user_id"],
                        "final_json_filename": user.get("final_json_filename"),
                        "final_json_updated": user.get("final_json_updated"),
                        "final_json_message_count": user.get("final_json_message_count", 0),
                        "first_seen": user.get("first_seen"),
                        "last_seen": user.get("last_seen")
                    })
                
                return users
                
        except Exception as e:
            logger.error(f"❌ Error listing processed users: {e}")
            return []

async def main():
    """تابع اصلی"""
    import argparse
    
    parser = argparse.ArgumentParser(description="User JSON Processor")
    parser.add_argument("--user-id", type=int, help="User ID to process")
    parser.add_argument("--list", action="store_true", help="List all processed users")
    parser.add_argument("--info", type=int, help="Get info for specific user")
    
    args = parser.parse_args()
    
    processor = UserJSONProcessor()
    
    if args.list:
        logger.info("📋 Listing all processed users...")
        users = await processor.list_processed_users()
        
        if not users:
            logger.info("📭 No processed users found")
        else:
            logger.info(f"📊 Found {len(users)} processed users:")
            for user in users:
                logger.info(f"👤 User {user['user_id']}: {user['final_json_filename']} ({user['final_json_message_count']} messages)")
    
    elif args.info:
        logger.info(f"🔍 Getting info for user {args.info}...")
        user_info = await processor.get_user_info(args.info)
        
        if user_info:
            logger.info(f"👤 User {args.info} info:")
            logger.info(f"   First seen: {user_info.get('first_seen')}")
            logger.info(f"   Last seen: {user_info.get('last_seen')}")
            logger.info(f"   Final JSON: {user_info.get('final_json_filename', 'None')}")
            logger.info(f"   Message count: {user_info.get('final_json_message_count', 0)}")
        else:
            logger.warning(f"⚠️ User {args.info} not found in database")
    
    elif args.user_id:
        logger.info(f"🔄 Processing user {args.user_id}...")
        success = await processor.process_user_json(args.user_id)
        
        if success:
            logger.info(f"✅ User {args.user_id} processed successfully")
        else:
            logger.error(f"❌ Failed to process user {args.user_id}")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 