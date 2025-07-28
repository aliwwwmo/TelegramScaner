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
    """سرویس MongoDB برای ذخیره اطلاعات گروه‌ها"""
    
    def __init__(self, connection_string: str = None, database_name: str = None, collection_name: str = None):
        """مقداردهی اولیه سرویس MongoDB"""
        self.connection_string = connection_string or MONGO_CONFIG.connection_string
        self.database_name = database_name or MONGO_CONFIG.database_name
        self.collection_name = collection_name or MONGO_CONFIG.collection_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        
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
            
            # ایجاد ایندکس‌ها برای بهینه‌سازی
            await self._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB: {self.database_name}.{self.collection_name}")
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