# User Storage Feature

## Overview
این ویژگی جدید امکان ذخیره user-id های استخراج شده در دیتابیس MongoDB را فراهم می‌کند. هر بار که کاربری از گروه‌ها یا پیام‌ها استخراج می‌شود، user-id آن در کالکشن `users` ذخیره می‌شود.

## Features

### 1. Automatic User ID Storage
- هر user-id که استخراج می‌شود به طور خودکار در دیتابیس ذخیره می‌شود
- فقط user-id ذخیره می‌شود، هیچ اطلاعات اضافی دیگری ذخیره نمی‌شود
- از تکرار user-id ها جلوگیری می‌شود

### 2. Database Collection
- کالکشن جدید `users` در دیتابیس MongoDB
- ساختار ساده: `{user_id, first_seen, last_seen}`
- ایندکس‌های بهینه برای جستجوی سریع

### 3. Integration Points
- **Member Extraction**: هنگام استخراج اعضای گروه
- **Message Analysis**: هنگام تحلیل پیام‌ها
- **User Tracking**: هنگام ردیابی کاربران

## Database Schema

### Users Collection
```json
{
  "user_id": 123456789,
  "first_seen": "2024-01-01T12:00:00Z",
  "last_seen": "2024-01-01T12:00:00Z"
}
```

### Indexes
- `user_id` (unique)
- `first_seen`
- `last_seen`

## API Methods

### MongoService Methods

#### `save_user_id(user_id: int) -> bool`
ذخیره یک user-id در دیتابیس

#### `save_multiple_user_ids(user_ids: List[int]) -> int`
ذخیره چندین user-id به صورت بهینه

#### `get_user_count() -> int`
دریافت تعداد کل کاربران

#### `get_recent_users(hours: int = 24) -> List[int]`
دریافت کاربرانی که در ساعات اخیر دیده شده‌اند

#### `get_user_stats() -> Dict[str, Any]`
دریافت آمار کاربران

## Configuration

### Environment Variables
```env
# MongoDB Settings
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups
USE_DATABASE_FOR_GROUPS=true
```

## Usage Examples

### Test User Storage
```bash
cd analyzer
python test_user_storage.py
```

### Check User Count
```python
async with MongoServiceManager() as mongo_service:
    user_count = await mongo_service.get_user_count()
    print(f"Total users: {user_count}")
```

### Get Recent Users
```python
async with MongoServiceManager() as mongo_service:
    recent_users = await mongo_service.get_recent_users(hours=24)
    print(f"Recent users: {len(recent_users)}")
```

## Integration Points

### 1. Telegram Client
- `get_chat_members()`: ذخیره user-id هنگام استخراج اعضا
- `get_chat_members_basic()`: ذخیره user-id از پیام‌ها

### 2. User Tracker
- `_add_user_to_group()`: ذخیره user-id هنگام اضافه کردن کاربر
- `_add_user_message()`: ذخیره user-id هنگام پردازش پیام
- `_create_user_structure()`: ذخیره user-id هنگام ایجاد کاربر جدید

## Benefits

1. **Minimal Storage**: فقط user-id ذخیره می‌شود
2. **No Duplicates**: از تکرار جلوگیری می‌شود
3. **Efficient**: استفاده از bulk operations
4. **Trackable**: امکان ردیابی زمان اولین و آخرین مشاهده
5. **Scalable**: قابلیت مقیاس‌پذیری بالا

## Monitoring

### Log Messages
- `✅ New user {user_id} saved to database`
- `✅ Updated user {user_id} last_seen`
- `✅ Saved {count} users to database`
- `💾 Saved {count} user IDs to database`

### Statistics
- تعداد کل کاربران
- کاربران جدید امروز
- کاربران جدید هفته گذشته
- کاربران اخیر (24 ساعت گذشته)

## Error Handling

- خطاهای اتصال به دیتابیس مدیریت می‌شوند
- خطاهای ذخیره‌سازی مانع ادامه کار نمی‌شوند
- لاگ‌های مناسب برای عیب‌یابی

## Future Enhancements

1. **User Analytics**: تحلیل رفتار کاربران
2. **Export Features**: امکان export کاربران
3. **Filtering**: فیلتر کردن بر اساس تاریخ
4. **Cleanup**: پاکسازی کاربران قدیمی
5. **Backup**: پشتیبان‌گیری از داده‌ها 