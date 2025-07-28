#!/usr/bin/env python3
"""
اسکریپت انتقال گروه‌ها از فایل links.txt به دیتابیس MongoDB
"""

import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from services.mongo_service import MongoServiceManager
from models.data_models import GroupInfo, ChatType
from config.settings import ANALYSIS_CONFIG
from utils.logger import logger

async def read_groups_from_file() -> list:
    """خواندن گروه‌ها از فایل links.txt"""
    logger.info("📄 Reading groups from links.txt file...")
    
    links_file = Path(ANALYSIS_CONFIG.links_file)
    if not links_file.exists():
        logger.error(f"❌ Links file not found: {links_file}")
        return []
    
    try:
        with open(links_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        logger.info(f"✅ Found {len(lines)} groups in links.txt")
        return lines
        
    except Exception as e:
        logger.error(f"❌ Error reading links.txt: {e}")
        return []

async def create_group_info_from_link(link: str) -> GroupInfo:
    """ایجاد GroupInfo از لینک"""
    # استخراج username از لینک
    username = None
    if link.startswith('@'):
        username = link[1:]  # حذف @
    elif 't.me/' in link:
        # استخراج username از لینک تلگرام
        parts = link.split('t.me/')
        if len(parts) > 1:
            username = parts[1].split('/')[0]
    
    # ایجاد GroupInfo موقت
    group_info = GroupInfo(
        chat_id=0,  # موقت - بعداً به‌روزرسانی می‌شود
        username=username,
        link=link,
        chat_type=ChatType.SUPERGROUP,  # پیش‌فرض
        is_public=bool(username)
    )
    
    return group_info

async def migrate_groups_to_database():
    """انتقال گروه‌ها از فایل به دیتابیس"""
    logger.info("🔄 Starting migration from links.txt to MongoDB...")
    
    # خواندن گروه‌ها از فایل
    file_groups = await read_groups_from_file()
    
    if not file_groups:
        logger.warning("⚠️ No groups found in links.txt file")
        return False
    
    try:
        async with MongoServiceManager() as mongo_service:
            # بررسی گروه‌های موجود در دیتابیس
            existing_groups = await mongo_service.get_all_groups()
            existing_links = {group.link for group in existing_groups if group.link}
            existing_usernames = {group.username for group in existing_groups if group.username}
            
            logger.info(f"📊 Found {len(existing_groups)} existing groups in database")
            
            # انتقال گروه‌های جدید
            migrated_count = 0
            skipped_count = 0
            
            for link in file_groups:
                # بررسی تکراری بودن
                if link in existing_links:
                    logger.info(f"⏭️ Skipping duplicate link: {link}")
                    skipped_count += 1
                    continue
                
                # استخراج username
                username = None
                if link.startswith('@'):
                    username = link[1:]
                elif 't.me/' in link:
                    parts = link.split('t.me/')
                    if len(parts) > 1:
                        username = parts[1].split('/')[0]
                
                if username and username in existing_usernames:
                    logger.info(f"⏭️ Skipping duplicate username: @{username}")
                    skipped_count += 1
                    continue
                
                # ایجاد GroupInfo
                group_info = GroupInfo(
                    chat_id=0,  # موقت
                    username=username,
                    link=link,
                    chat_type=ChatType.SUPERGROUP,
                    is_public=bool(username)
                )
                
                # ذخیره در دیتابیس
                if await mongo_service.save_group_info(group_info):
                    logger.info(f"✅ Migrated: {link}")
                    migrated_count += 1
                else:
                    logger.error(f"❌ Failed to migrate: {link}")
            
            # نمایش آمار
            logger.info(f"\n📊 Migration Summary:")
            logger.info(f"   📄 Groups in file: {len(file_groups)}")
            logger.info(f"   💾 Groups in database: {len(existing_groups)}")
            logger.info(f"   ✅ Migrated: {migrated_count}")
            logger.info(f"   ⏭️ Skipped (duplicates): {skipped_count}")
            logger.info(f"   📈 Total in database after migration: {len(existing_groups) + migrated_count}")
            
            return migrated_count > 0
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

async def backup_links_file():
    """پشتیبان‌گیری از فایل links.txt"""
    logger.info("💾 Creating backup of links.txt...")
    
    links_file = Path(ANALYSIS_CONFIG.links_file)
    if not links_file.exists():
        logger.warning("⚠️ Links file not found, skipping backup")
        return
    
    try:
        backup_file = links_file.with_suffix('.txt.backup')
        import shutil
        shutil.copy2(links_file, backup_file)
        logger.info(f"✅ Backup created: {backup_file}")
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")

async def main():
    """تابع اصلی"""
    logger.info("🚀 Starting groups migration...")
    
    # پشتیبان‌گیری از فایل
    await backup_links_file()
    
    # انتقال گروه‌ها
    success = await migrate_groups_to_database()
    
    if success:
        logger.info("\n🎉 Migration completed successfully!")
        logger.info("💡 You can now set USE_DATABASE_FOR_GROUPS=true in your .env file")
    else:
        logger.error("\n❌ Migration failed!")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 