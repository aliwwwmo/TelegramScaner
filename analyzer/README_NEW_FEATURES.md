# قابلیت‌های جدید - User JSON Processor

## خلاصه

این قابلیت جدید امکان ترکیب فایل‌های JSON کاربران از Saved Messages و ایجاد فایل نهایی را فراهم می‌کند. برنامه به صورت هوشمند فایل‌های جدید را شناسایی کرده و فقط آن‌ها را با فایل نهایی قبلی ترکیب می‌کند.

## فایل‌های جدید

### 1. `services/user_json_manager.py`
سرویس اصلی برای مدیریت فایل‌های JSON کاربران از Saved Messages

**ویژگی‌ها:**
- جستجوی فایل‌های JSON در Saved Messages
- ترکیب خودکار فایل‌های یک کاربر
- ارسال فایل نهایی به Saved Messages
- مدیریت فایل‌های موقت

### 2. `user_json_processor.py`
اسکریپت اصلی برای پردازش فایل‌های JSON کاربران

**دستورات:**
```bash
# پردازش یک کاربر
python user_json_processor.py --user-id 123456789

# مشاهده لیست کاربران پردازش شده
python user_json_processor.py --list

# دریافت اطلاعات یک کاربر
python user_json_processor.py --info 123456789
```

### 3. `quick_user_process.py`
اسکریپت سریع برای پردازش یک کاربر

```bash
python quick_user_process.py 123456789
```

### 4. `test_user_json_processor.py`
اسکریپت تست برای بررسی عملکرد قابلیت‌ها

```bash
python test_user_json_processor.py
```

## به‌روزرسانی‌های موجود

### `services/mongo_service.py`
متدهای جدید اضافه شده:

- `save_user_final_json_filename()`: ذخیره نام فایل نهایی
- `get_user_final_json_filename()`: دریافت نام فایل نهایی
- `update_user_final_json_info()`: به‌روزرسانی اطلاعات فایل نهایی

## نحوه کارکرد

### 1. جستجوی فایل‌ها
```python
user_files = await json_manager.get_user_json_files(user_id)
```

### 2. ترکیب فایل‌ها
```python
success, merged_data, final_filename = await json_manager.merge_user_json_files(user_id)
```

### 3. ارسال فایل نهایی
```python
sent = await json_manager.send_final_json(merged_data, final_filename)
```

### 4. ذخیره در دیتابیس
```python
saved = await mongo_service.update_user_final_json_info(user_id, final_filename, message_count)
```

## ساختار فایل‌ها

### فایل‌های ورودی
```
user_id_group_id_YYYYMMDD_HHMMSS_uuid.json
```

### فایل‌های نهایی
```
final_user_id_YYYYMMDD_HHMMSS_uuid.json
```

## ساختار دیتابیس

### کالکشن users
```json
{
  "user_id": 123456789,
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2024-01-01T12:00:00Z",
  "final_json_filename": "final_123456789_20240101_120000_abc12345.json",
  "final_json_updated": "2024-01-01T12:00:00Z",
  "final_json_message_count": 150
}
```

## مثال استفاده

### پردازش یک کاربر
```bash
cd analyzer
python user_json_processor.py --user-id 123456789
```

### خروجی نمونه
```
🔍 Starting JSON processing for user 123456789
✅ Found 5 JSON files for user 123456789
✅ Merged 150 messages for user 123456789
✅ Final JSON sent: final_123456789_20240101_120000_abc12345.json
✅ Successfully processed user 123456789
📊 Final JSON: final_123456789_20240101_120000_abc12345.json
📝 Total messages: 150
```

## نکات مهم

1. **فایل‌های موقت**: فایل‌های موقت در حین پردازش ایجاد و حذف می‌شوند
2. **محدودیت پیام‌ها**: حداکثر 1000 پیام از Saved Messages بررسی می‌شود
3. **بهینه‌سازی**: فقط فایل‌های جدیدتر از فایل نهایی ترکیب می‌شوند
4. **خطاها**: در صورت بروز خطا، لاگ‌های مناسب ثبت می‌شود

## پیش‌نیازها

- اتصال به MongoDB
- تنظیمات صحیح Telegram API
- دسترسی به Saved Messages
- فایل‌های JSON موجود در Saved Messages

## تست

برای تست قابلیت‌ها:

```bash
# تست کامل
python test_user_json_processor.py

# تست سریع یک کاربر
python quick_user_process.py 123456789
```

## مستندات بیشتر

- `USER_JSON_PROCESSOR.md`: مستندات تفصیلی قابلیت
- `README.md`: مستندات اصلی پروژه 