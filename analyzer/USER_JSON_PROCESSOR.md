# User JSON Processor

این قابلیت جدید امکان ترکیب فایل‌های JSON کاربران از Saved Messages و ایجاد فایل نهایی را فراهم می‌کند.

## ویژگی‌ها

- 🔍 جستجوی فایل‌های JSON کاربران در Saved Messages
- 🔄 ترکیب خودکار فایل‌های JSON یک کاربر
- 📊 ذخیره اطلاعات فایل نهایی در دیتابیس MongoDB
- ⚡ بهینه‌سازی: فقط فایل‌های جدید را ترکیب می‌کند
- 📋 مدیریت فایل‌های نهایی با پیشوند `final_`

## نحوه کارکرد

### 1. جستجوی فایل‌ها
برنامه تمام فایل‌های JSON در Saved Messages را بررسی می‌کند و فایل‌های مربوط به کاربر مورد نظر را پیدا می‌کند.

### 2. ترکیب فایل‌ها
- اگر فایل نهایی قبلاً وجود دارد، فقط فایل‌های جدید را اضافه می‌کند
- اگر فایل نهایی وجود ندارد، تمام فایل‌ها را ترکیب می‌کند

### 3. ذخیره در دیتابیس
نام فایل نهایی و اطلاعات مربوطه در کالکشن `users` در MongoDB ذخیره می‌شود.

## استفاده

### پردازش یک کاربر
```bash
python user_json_processor.py --user-id 123456789
```

### مشاهده لیست کاربران پردازش شده
```bash
python user_json_processor.py --list
```

### دریافت اطلاعات یک کاربر
```bash
python user_json_processor.py --info 123456789
```

## ساختار فایل‌ها

### فایل‌های ورودی
فایل‌های JSON با فرمت: `user_id_group_id_YYYYMMDD_HHMMSS_uuid.json`

### فایل نهایی
فایل نهایی با فرمت: `final_user_id_YYYYMMDD_HHMMSS_uuid.json`

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

## مثال خروجی

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