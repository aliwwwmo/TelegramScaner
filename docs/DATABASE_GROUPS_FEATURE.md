# ویژگی خواندن گروه‌ها از دیتابیس MongoDB

## خلاصه تغییرات

این ویژگی جدید امکان خواندن گروه‌ها را از دیتابیس MongoDB به جای فایل `links.txt` فراهم می‌کند.

## تنظیمات جدید

### متغیر محیطی جدید
```bash
USE_DATABASE_FOR_GROUPS=true
```

- `true`: گروه‌ها از دیتابیس MongoDB خوانده می‌شوند
- `false`: گروه‌ها از فایل `links.txt` خوانده می‌شوند

## نحوه کارکرد

### 1. خواندن از دیتابیس (پیش‌فرض)
وقتی `USE_DATABASE_FOR_GROUPS=true` باشد:
- برنامه ابتدا سعی می‌کند گروه‌ها را از دیتابیس MongoDB بخواند
- اگر گروهی در دیتابیس نباشد، به فایل `links.txt` برمی‌گردد
- اگر هیچ منبعی در دسترس نباشد، خطا می‌دهد

### 2. خواندن از فایل
وقتی `USE_DATABASE_FOR_GROUPS=false` باشد:
- برنامه ابتدا سعی می‌کند گروه‌ها را از فایل `links.txt` بخواند
- اگر فایل موجود نباشد، به دیتابیس MongoDB برمی‌گردد
- اگر هیچ منبعی در دسترس نباشد، خطا می‌دهد

## مزایا

1. **مدیریت بهتر گروه‌ها**: گروه‌ها در دیتابیس ذخیره می‌شوند و قابل مدیریت هستند
2. **عدم وابستگی به فایل**: نیازی به نگهداری فایل `links.txt` نیست
3. **قابلیت جستجو**: می‌توان گروه‌ها را بر اساس معیارهای مختلف جستجو کرد
4. **آمار و گزارش**: امکان دریافت آمار از گروه‌های ذخیره شده

## نحوه استفاده

### 1. فعال‌سازی خواندن از دیتابیس
```bash
# در فایل .env
USE_DATABASE_FOR_GROUPS=true
```

### 2. غیرفعال‌سازی و استفاده از فایل
```bash
# در فایل .env
USE_DATABASE_FOR_GROUPS=false
```

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

## توابع جدید

### در `mongo_service.py`:
- `get_all_groups()`: دریافت تمام گروه‌ها
- `get_groups_by_type()`: دریافت گروه‌ها بر اساس نوع

### در `main.py`:
- `get_groups_from_database()`: خواندن گروه‌ها از دیتابیس
- `get_groups_from_file()`: خواندن گروه‌ها از فایل

## نکات مهم

1. **اولویت دیتابیس**: اگر `USE_DATABASE_FOR_GROUPS=true` باشد، ابتدا دیتابیس بررسی می‌شود
2. **فال‌بک**: در صورت عدم وجود گروه در منبع اول، منبع دوم بررسی می‌شود
3. **سازگاری**: این تغییر با کد قبلی سازگار است و فایل `links.txt` همچنان قابل استفاده است
4. **لاگ**: تمام عملیات در لاگ‌ها ثبت می‌شود

## مثال استفاده

```python
# خواندن گروه‌ها از دیتابیس
async with MongoServiceManager() as mongo_service:
    groups = await mongo_service.get_all_groups()
    for group in groups:
        print(f"Group: {group.username} - {group.link}")
```

## عیب‌یابی

اگر با مشکل مواجه شدید:

1. **خطای `_id`**: مدل `GroupInfo` اصلاح شده است تا فیلد `_id` MongoDB را نادیده بگیرد
2. **دیتابیس خالی**: از اسکریپت `migrate_groups_to_db.py` برای انتقال گروه‌ها استفاده کنید
3. **اتصال MongoDB**: تنظیمات اتصال را در فایل `.env` بررسی کنید

## تنظیمات MongoDB

اطمینان حاصل کنید که تنظیمات MongoDB در فایل `.env` درست باشد:

```bash
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups
``` 