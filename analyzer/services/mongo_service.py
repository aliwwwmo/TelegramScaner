import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config.settings import MONGO_CONFIG
from models.data_models import GroupInfo, ChatType, ScanStatus
from utils.logger import logger

class MongoService:
    """سرویس MongoDB برای ذخیره اطلاعات گروه‌ها و کاربران"""
    
    def __init__(self, connection_string: str = None, database_name: str = None, collection_name: str = None):
        """مقداردهی اولیه سرویس MongoDB"""
        self.connection_string = connection_string or MONGO_CONFIG.connection_string
        self.database_name = database_name or MONGO_CONFIG.database_name
        self.collection_name = collection_name or MONGO_CONFIG.collection_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        self.users_collection = None  # کالکشن جدید برای کاربران
        
    async def connect(self) -> bool:
        """اتصال به MongoDB"""
        try:
            # ایجاد اتصال
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # تست اتصال
            self.client.admin.command('ping')
            
            # انتخاب دیتابیس و کالکشن
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            self.users_collection = self.db['users']  # کالکشن جدید برای کاربران
            
            # ایجاد ایندکس‌ها برای بهینه‌سازی
            await self._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB: {self.database_name}.{self.collection_name}")
            logger.info(f"✅ Users collection ready: {self.database_name}.users")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            return False
    
    async def _create_indexes(self):
        """ایجاد ایندکس‌های بهینه"""
        try:
            # ایندکس برای جستجوی سریع بر اساس chat_id
            self.collection.create_index("chat_id", unique=True)
            
            # ایندکس برای جستجو بر اساس username
            self.collection.create_index("username", sparse=True)
            
            # ایندکس برای جستجو بر اساس last_scan_time
            self.collection.create_index("last_scan_time")
            
            # ایندکس برای جستجو بر اساس last_scan_status
            self.collection.create_index("last_scan_status")
            
            # ایندکس‌های جدید برای کالکشن کاربران
            if self.users_collection:
                self.users_collection.create_index("user_id", unique=True)
                self.users_collection.create_index("first_seen")
                self.users_collection.create_index("last_seen")
            
            logger.info("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create indexes: {e}")
    
    async def disconnect(self):
        """قطع اتصال از MongoDB"""
        if self.client:
            self.client.close()
            logger.info("✅ Disconnected from MongoDB")
    
    async def save_group_info(self, group_info: GroupInfo) -> bool:
        """ذخیره یا به‌روزرسانی اطلاعات گروه"""
        try:
            if self.collection is None:
                logger.error("❌ MongoDB not connected")
                return False
            
            # تبدیل به دیکشنری
            data = group_info.to_dict()
            
            # استفاده از upsert برای به‌روزرسانی یا درج
            result = self.collection.update_one(
                {"chat_id": group_info.chat_id},
                {"$set": data},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"✅ New group saved: {group_info.chat_id}")
            else:
                logger.info(f"✅ Group updated: {group_info.chat_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save group info: {e}")
            return False
    
    async def get_group_info(self, chat_id: int) -> Optional[GroupInfo]:
        """دریافت اطلاعات گروه بر اساس chat_id"""
        try:
            if self.collection is None:
                return None
            
            data = self.collection.find_one({"chat_id": chat_id})
            if data:
                return GroupInfo.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get group info: {e}")
            return None
    
    async def get_group_by_username(self, username: str) -> Optional[GroupInfo]:
        """دریافت اطلاعات گروه بر اساس username"""
        try:
            if self.collection is None:
                return None
            
            data = self.collection.find_one({"username": username})
            if data:
                return GroupInfo.from_dict(data)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get group by username: {e}")
            return None
    
    async def get_groups_by_status(self, status: ScanStatus) -> List[GroupInfo]:
        """دریافت گروه‌ها بر اساس وضعیت اسکن"""
        try:
            if self.collection is None:
                return []
            
            cursor = self.collection.find({"last_scan_status": status.value})
            groups = []
            for data in cursor:
                groups.append(GroupInfo.from_dict(data))
            
            return groups
            
        except Exception as e:
            logger.error(f"❌ Failed to get groups by status: {e}")
            return []
    
    async def get_recent_scans(self, hours: int = 24) -> List[GroupInfo]:
        """دریافت گروه‌هایی که در ساعات اخیر اسکن شده‌اند"""
        try:
            if self.collection is None:
                return []
            
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            cursor = self.collection.find({
                "last_scan_time": {"$gte": cutoff_time}
            }).sort("last_scan_time", -1)
            
            groups = []
            for data in cursor:
                groups.append(GroupInfo.from_dict(data))
            
            return groups
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent scans: {e}")
            return []
    
    async def get_failed_scans(self) -> List[GroupInfo]:
        """دریافت گروه‌هایی که اسکن آنها ناموفق بوده"""
        return await self.get_groups_by_status(ScanStatus.FAILED)
    
    async def get_successful_scans(self) -> List[GroupInfo]:
        """دریافت گروه‌هایی که اسکن آنها موفق بوده"""
        return await self.get_groups_by_status(ScanStatus.SUCCESS)
    
    async def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار کلی"""
        try:
            if self.collection is None:
                return {}
            
            total_groups = self.collection.count_documents({})
            successful_scans = self.collection.count_documents({"last_scan_status": ScanStatus.SUCCESS.value})
            failed_scans = self.collection.count_documents({"last_scan_status": ScanStatus.FAILED.value})
            
            # آمار بر اساس نوع چت
            channel_count = self.collection.count_documents({"chat_type": ChatType.CHANNEL.value})
            group_count = self.collection.count_documents({"chat_type": ChatType.GROUP.value})
            supergroup_count = self.collection.count_documents({"chat_type": ChatType.SUPERGROUP.value})
            
            # آمار بر اساس public/private
            public_count = self.collection.count_documents({"is_public": True})
            private_count = self.collection.count_documents({"is_public": False})
            
            return {
                "total_groups": total_groups,
                "successful_scans": successful_scans,
                "failed_scans": failed_scans,
                "success_rate": (successful_scans / total_groups * 100) if total_groups > 0 else 0,
                "channels": channel_count,
                "groups": group_count,
                "supergroups": supergroup_count,
                "public": public_count,
                "private": private_count
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}
    
    async def delete_group(self, chat_id: int) -> bool:
        """حذف گروه از دیتابیس"""
        try:
            if self.collection is None:
                return False
            
            result = self.collection.delete_one({"chat_id": chat_id})
            if result.deleted_count > 0:
                logger.info(f"✅ Group deleted: {chat_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete group: {e}")
            return False
    
    async def cleanup_old_records(self, days: int = 30) -> int:
        """پاک کردن رکوردهای قدیمی"""
        try:
            if self.collection is None:
                return 0
            
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            result = self.collection.delete_many({
                "updated_at": {"$lt": cutoff_time}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"✅ Cleaned up {deleted_count} old records")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old records: {e}")
            return 0

    async def get_all_groups(self) -> List[GroupInfo]:
        """دریافت تمام گروه‌ها از دیتابیس"""
        try:
            if self.collection is None:
                logger.error("❌ MongoDB not connected")
                return []
            
            cursor = self.collection.find({})
            groups = []
            for data in cursor:
                try:
                    group_info = GroupInfo.from_dict(data)
                    groups.append(group_info)
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse group data: {e}")
                    continue
            
            logger.info(f"✅ Retrieved {len(groups)} groups from MongoDB")
            return groups
            
        except Exception as e:
            logger.error(f"❌ Failed to get all groups: {e}")
            return []
    
    async def get_groups_by_type(self, chat_type: ChatType) -> List[GroupInfo]:
        """دریافت گروه‌ها بر اساس نوع چت"""
        try:
            if self.collection is None:
                return []
            
            cursor = self.collection.find({"chat_type": chat_type.value})
            groups = []
            for data in cursor:
                try:
                    group_info = GroupInfo.from_dict(data)
                    groups.append(group_info)
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse group data: {e}")
                    continue
            
            logger.info(f"✅ Retrieved {len(groups)} {chat_type.value} groups from MongoDB")
            return groups
            
        except Exception as e:
            logger.error(f"❌ Failed to get groups by type: {e}")
            return []

    async def save_user_id(self, user_id: int) -> bool:
        """ذخیره user_id در کالکشن users"""
        try:
            if self.users_collection is None:
                logger.error("❌ MongoDB users collection not connected")
                return False
            
            # بررسی اینکه آیا کاربر قبلاً وجود دارد
            existing_user = self.users_collection.find_one({"user_id": user_id})
            
            if existing_user:
                # به‌روزرسانی last_seen
                result = self.users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"last_seen": datetime.utcnow()}}
                )
                if result.modified_count > 0:
                    logger.debug(f"✅ Updated user {user_id} last_seen")
            else:
                # درج کاربر جدید
                user_data = {
                    "user_id": user_id,
                    "first_seen": datetime.utcnow(),
                    "last_seen": datetime.utcnow()
                }
                result = self.users_collection.insert_one(user_data)
                if result.inserted_id:
                    logger.debug(f"✅ New user {user_id} saved to database")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save user {user_id}: {e}")
            return False
    
    async def save_multiple_user_ids(self, user_ids: List[int]) -> int:
        """ذخیره چندین user_id به صورت بهینه"""
        try:
            if self.users_collection is None:
                logger.error("❌ MongoDB users collection not connected")
                return 0
            
            if not user_ids:
                return 0
            
            current_time = datetime.utcnow()
            saved_count = 0
            
            # استفاده از bulk operations برای بهینه‌سازی
            bulk_operations = []
            
            for user_id in user_ids:
                # بررسی اینکه آیا کاربر قبلاً وجود دارد
                existing_user = self.users_collection.find_one({"user_id": user_id})
                
                if existing_user:
                    # به‌روزرسانی last_seen
                    bulk_operations.append(
                        pymongo.UpdateOne(
                            {"user_id": user_id},
                            {"$set": {"last_seen": current_time}},
                            upsert=False
                        )
                    )
                else:
                    # درج کاربر جدید
                    user_data = {
                        "user_id": user_id,
                        "first_seen": current_time,
                        "last_seen": current_time
                    }
                    bulk_operations.append(
                        pymongo.InsertOne(user_data)
                    )
            
            if bulk_operations:
                result = self.users_collection.bulk_write(bulk_operations, ordered=False)
                saved_count = result.upserted_count + result.modified_count
                logger.info(f"✅ Saved {saved_count} users to database")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"❌ Failed to save multiple users: {e}")
            return 0
    
    async def get_user_count(self) -> int:
        """دریافت تعداد کل کاربران"""
        try:
            if self.users_collection is None:
                return 0
            
            return self.users_collection.count_documents({})
            
        except Exception as e:
            logger.error(f"❌ Failed to get user count: {e}")
            return 0
    
    async def get_recent_users(self, hours: int = 24) -> List[int]:
        """دریافت کاربرانی که در ساعات اخیر دیده شده‌اند"""
        try:
            if self.users_collection is None:
                return []
            
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            cursor = self.users_collection.find({
                "last_seen": {"$gte": cutoff_time}
            }).sort("last_seen", -1)
            
            user_ids = [doc["user_id"] for doc in cursor]
            return user_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent users: {e}")
            return []
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """دریافت آمار کاربران"""
        try:
            if self.users_collection is None:
                return {}
            
            total_users = self.users_collection.count_documents({})
            
            # کاربران امروز
            from datetime import timedelta
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_users = self.users_collection.count_documents({
                "first_seen": {"$gte": today}
            })
            
            # کاربران هفته گذشته
            week_ago = datetime.utcnow() - timedelta(days=7)
            week_users = self.users_collection.count_documents({
                "first_seen": {"$gte": week_ago}
            })
            
            return {
                "total_users": total_users,
                "today_new_users": today_users,
                "week_new_users": week_users
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user stats: {e}")
            return {}

class MongoServiceManager:
    """مدیر اتصال MongoDB"""
    
    def __init__(self):
        self.service = MongoService()
    
    async def __aenter__(self):
        """ورود به context manager"""
        await self.service.connect()
        return self.service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """خروج از context manager"""
        await self.service.disconnect() 