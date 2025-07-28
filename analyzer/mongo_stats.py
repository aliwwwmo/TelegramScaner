#!/usr/bin/env python3
"""
ابزار مدیریت و مشاهده آمار MongoDB
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# اضافه کردن مسیر ریشه پروژه
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import MONGO_CONFIG
from services.mongo_service import MongoServiceManager
from models.data_models import ScanStatus, ChatType
from utils.logger import logger

async def show_stats():
    """نمایش آمار کلی"""
    async with MongoServiceManager() as mongo_service:
        stats = await mongo_service.get_stats()
        
        print("\n" + "="*50)
        print("📊 آمار کلی دیتابیس MongoDB")
        print("="*50)
        
        if not stats:
            print("❌ خطا در دریافت آمار")
            return
        
        print(f"📈 کل گروه‌ها: {stats.get('total_groups', 0)}")
        print(f"✅ اسکن‌های موفق: {stats.get('successful_scans', 0)}")
        print(f"❌ اسکن‌های ناموفق: {stats.get('failed_scans', 0)}")
        print(f"📊 نرخ موفقیت: {stats.get('success_rate', 0):.1f}%")
        print()
        
        print("📋 تفکیک بر اساس نوع:")
        print(f"   📢 کانال‌ها: {stats.get('channels', 0)}")
        print(f"   👥 گروه‌ها: {stats.get('groups', 0)}")
        print(f"   🏢 سوپرگروه‌ها: {stats.get('supergroups', 0)}")
        print()
        
        print("🔒 تفکیک بر اساس دسترسی:")
        print(f"   🌐 عمومی: {stats.get('public', 0)}")
        print(f"   🔐 خصوصی: {stats.get('private', 0)}")

async def show_recent_scans(hours: int = 24):
    """نمایش اسکن‌های اخیر"""
    async with MongoServiceManager() as mongo_service:
        recent_groups = await mongo_service.get_recent_scans(hours)
        
        print(f"\n🕒 اسکن‌های {hours} ساعت اخیر:")
        print("-" * 50)
        
        if not recent_groups:
            print("📭 هیچ اسکنی در این بازه زمانی یافت نشد")
            return
        
        for group in recent_groups:
            status_emoji = "✅" if group.last_scan_status == ScanStatus.SUCCESS else "❌"
            type_emoji = "📢" if group.chat_type == ChatType.CHANNEL else "👥"
            access_emoji = "🌐" if group.is_public else "🔐"
            
            print(f"{status_emoji} {type_emoji} {access_emoji} ID: {group.chat_id}")
            if group.username:
                print(f"   Username: @{group.username}")
            print(f"   آخرین اسکن: {group.last_scan_time.strftime('%Y-%m-%d %H:%M:%S') if group.last_scan_time else 'نامشخص'}")
            print(f"   تعداد اسکن: {group.scan_count}")
            print()

async def show_failed_scans():
    """نمایش اسکن‌های ناموفق"""
    async with MongoServiceManager() as mongo_service:
        failed_groups = await mongo_service.get_failed_scans()
        
        print("\n❌ اسکن‌های ناموفق:")
        print("-" * 50)
        
        if not failed_groups:
            print("✅ هیچ اسکن ناموفقی یافت نشد")
            return
        
        for group in failed_groups:
            type_emoji = "📢" if group.chat_type == ChatType.CHANNEL else "👥"
            access_emoji = "🌐" if group.is_public else "🔐"
            
            print(f"{type_emoji} {access_emoji} ID: {group.chat_id}")
            if group.username:
                print(f"   Username: @{group.username}")
            if group.link:
                print(f"   Link: {group.link}")
            print(f"   آخرین تلاش: {group.last_scan_time.strftime('%Y-%m-%d %H:%M:%S') if group.last_scan_time else 'نامشخص'}")
            print()

async def cleanup_old_records(days: int = 30):
    """پاک کردن رکوردهای قدیمی"""
    async with MongoServiceManager() as mongo_service:
        deleted_count = await mongo_service.cleanup_old_records(days)
        
        if deleted_count > 0:
            print(f"✅ {deleted_count} رکورد قدیمی پاک شد")
        else:
            print("📭 هیچ رکورد قدیمی برای پاک کردن یافت نشد")

async def search_group(search_term: str):
    """جستجو در گروه‌ها"""
    async with MongoServiceManager() as mongo_service:
        # جستجو بر اساس username
        if search_term.startswith('@'):
            search_term = search_term[1:]
        
        group = await mongo_service.get_group_by_username(search_term)
        
        if group:
            print(f"\n🔍 نتیجه جستجو برای '{search_term}':")
            print("-" * 50)
            print(f"🆔 ID: {group.chat_id}")
            print(f"👤 Username: @{group.username}")
            print(f"🔗 Link: {group.link}")
            print(f"📊 نوع: {group.chat_type.value}")
            print(f"🔒 دسترسی: {'عمومی' if group.is_public else 'خصوصی'}")
            print(f"📅 آخرین اسکن: {group.last_scan_time.strftime('%Y-%m-%d %H:%M:%S') if group.last_scan_time else 'نامشخص'}")
            print(f"✅ وضعیت: {group.last_scan_status.value}")
            print(f"🔢 تعداد اسکن: {group.scan_count}")
        else:
            print(f"❌ گروهی با نام '{search_term}' یافت نشد")

async def main():
    """تابع اصلی"""
    if len(sys.argv) < 2:
        print("""
🔧 ابزار مدیریت MongoDB

استفاده:
  python mongo_stats.py stats                    # نمایش آمار کلی
  python mongo_stats.py recent [hours]          # اسکن‌های اخیر (پیش‌فرض: 24 ساعت)
  python mongo_stats.py failed                  # اسکن‌های ناموفق
  python mongo_stats.py cleanup [days]          # پاک کردن رکوردهای قدیمی (پیش‌فرض: 30 روز)
  python mongo_stats.py search <username>       # جستجو در گروه‌ها
        """)
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "stats":
            await show_stats()
        
        elif command == "recent":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            await show_recent_scans(hours)
        
        elif command == "failed":
            await show_failed_scans()
        
        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            await cleanup_old_records(days)
        
        elif command == "search":
            if len(sys.argv) < 3:
                print("❌ لطفاً نام کاربری را وارد کنید")
                return
            search_term = sys.argv[2]
            await search_group(search_term)
        
        else:
            print(f"❌ دستور نامشخص: {command}")
    
    except Exception as e:
        logger.error(f"❌ خطا: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 