# راهنمای سریع - ویژگی دیتابیس گروه‌ها

## خلاصه تغییرات

برنامه حالا می‌تواند گروه‌ها را از دیتابیس MongoDB بخواند به جای فایل `links.txt`.

## تنظیمات سریع

### 1. فعال‌سازی خواندن از دیتابیس
```bash
# در فایل .env
USE_DATABASE_FOR_GROUPS=true
```

### 2. انتقال گروه‌ها از فایل به دیتابیس
```bash
python analyzer/migrate_groups_to_db.py
```

### 3. اجرای برنامه
```bash
python analyzer/main.py
```

## نحوه کارکرد

### حالت دیتابیس (پیش‌فرض)
- برنامه ابتدا گروه‌ها را از دیتابیس MongoDB می‌خواند
- اگر دیتابیس خالی باشد، به فایل `links.txt` برمی‌گردد
- اگر هیچ منبعی در دسترس نباشد، خطا می‌دهد

### حالت فایل
```bash
# در فایل .env
USE_DATABASE_FOR_GROUPS=false
```

## مزایا

1. **مدیریت بهتر گروه‌ها** در دیتابیس
2. **عدم وابستگی به فایل** `links.txt`
3. **قابلیت جستجو** در گروه‌ها
4. **سازگاری کامل** با کد قبلی
5. **فال‌بک خودکار** بین دیتابیس و فایل

## ساختار دیتابیس

گروه‌ها در کالکشن `groups` با ساختار زیر ذخیره می‌شوند:

```json
{
  "chat_id": -1001234567890,
  "username": "example_group",
  "link": "https://t.me/example_group",
  "chat_type": "supergroup",
  "is_public": true,
  "last_scan_time": "2024-01-01T00:00:00Z",
  "last_scan_status": "success",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## تنظیمات MongoDB

```bash
# در فایل .env
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups
USE_DATABASE_FOR_GROUPS=true
```

## عیب‌یابی سریع

### مشکل: گروه‌ها از دیتابیس خوانده نمی‌شوند
**راه حل:** گروه‌ها را از فایل به دیتابیس منتقل کنید:
```bash
python analyzer/migrate_groups_to_db.py
```

### مشکل: خطای `_id`
**راه حل:** مدل `GroupInfo` اصلاح شده است و این مشکل حل شده است.

### مشکل: دیتابیس خالی
**راه حل:** ابتدا گروه‌ها را در فایل `links.txt` قرار دهید، سپس منتقل کنید.

## خروجی مورد انتظار

```
🔍 Using database as source for groups...
✅ Retrieved 5 group links from database
📋 Found 5 chat(s) to analyze
🔍 Analyzing chat 1/5
   Original: https://t.me/example_group
   Resolved: https://t.me/example_group
✅ Chat 1 completed successfully
```

## نکات مهم

1. **اولویت دیتابیس**: اگر `USE_DATABASE_FOR_GROUPS=true` باشد، ابتدا دیتابیس بررسی می‌شود
2. **فال‌بک**: در صورت عدم وجود گروه در منبع اول، منبع دوم بررسی می‌شود
3. **سازگاری**: این تغییر با کد قبلی سازگار است
4. **لاگ**: تمام عملیات در لاگ‌ها ثبت می‌شود

## مستندات کامل

برای اطلاعات بیشتر، فایل `DATABASE_GROUPS_FEATURE.md` را مطالعه کنید. 