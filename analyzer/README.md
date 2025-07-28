# Telegram Chat Analyzer

یک ابزار قدرتمند برای تحلیل گروه‌ها و کانال‌های تلگرام با قابلیت استخراج اطلاعات کاربران، پیام‌ها و لینک‌ها.

## ویژگی‌های جدید

### 🔄 خواندن گروه‌ها از دیتابیس MongoDB
- امکان خواندن گروه‌ها از دیتابیس MongoDB به جای فایل `links.txt`
- مدیریت بهتر گروه‌ها و قابلیت جستجو
- تنظیم `USE_DATABASE_FOR_GROUPS=true` در فایل `.env`

## نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.8+
- MongoDB
- Docker (اختیاری)

### نصب
```bash
# کلون کردن پروژه
git clone <repository-url>
cd TelegramScaner

# نصب وابستگی‌ها
pip install -r requirements.txt

# کپی کردن فایل تنظیمات
cp env.example .env

# ویرایش تنظیمات
nano .env
```

### تنظیمات MongoDB
```bash
# در فایل .env
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups
USE_DATABASE_FOR_GROUPS=true
```

## استفاده

### 1. تنظیم API تلگرام
```bash
# در فایل .env
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
```

### 2. انتخاب منبع گروه‌ها

#### استفاده از دیتابیس (پیشنهادی)
```bash
USE_DATABASE_FOR_GROUPS=true
```

#### استفاده از فایل
```bash
USE_DATABASE_FOR_GROUPS=false
# گروه‌ها در فایل links.txt قرار می‌گیرند
```

### 3. اجرای برنامه
```bash
# اجرای آنالایزر
python analyzer/main.py

# انتقال گروه‌ها از فایل به دیتابیس
python analyzer/migrate_groups_to_db.py
```

## ویژگی‌ها

### 📊 تحلیل گروه‌ها
- استخراج اطلاعات کامل گروه‌ها
- تحلیل پیام‌ها و کاربران
- استخراج لینک‌ها از پیام‌ها
- ردیابی واکنش‌ها و فورواردها

### 👥 مدیریت کاربران
- استخراج اطلاعات کاربران
- ردیابی فعالیت‌ها
- ذخیره در تلگرام (Saved Messages)

### 🔗 تحلیل لینک‌ها
- استخراج لینک‌ها از پیام‌ها
- اعتبارسنجی لینک‌ها
- ذخیره جداگانه لینک‌ها

### 💾 ذخیره‌سازی
- ذخیره در MongoDB
- پشتیبان‌گیری خودکار
- گزارش‌گیری

## ساختار پروژه

```
analyzer/
├── config/          # تنظیمات
├── core/           # هسته برنامه
├── models/         # مدل‌های داده
├── services/       # سرویس‌ها
├── utils/          # ابزارها
├── main.py         # فایل اصلی
├── test_database_groups.py  # تست دیتابیس
└── migrate_groups_to_db.py  # انتقال گروه‌ها
```

## تنظیمات پیشرفته

### تنظیمات پیام‌ها
```bash
MESSAGE_LIMIT=100
MESSAGE_BATCH_SIZE=200
DELAY_BETWEEN_BATCHES=0
```

### تنظیمات اعضا
```bash
MEMBER_LIMIT=0
MEMBER_BATCH_SIZE=500
GET_MEMBERS=true
INCLUDE_BOTS=true
```

### تنظیمات تحلیل
```bash
EXTRACT_ALL_MESSAGES=true
EXTRACT_ALL_MEMBERS=true
EXTRACT_MEDIA_INFO=true
EXTRACT_REACTIONS=true
SAVE_MESSAGE_TEXT=true
ANALYZE_MEDIA=true
TRACK_REACTIONS=true
TRACK_FORWARDS=true
DEEP_SCAN=true
```

## Docker

### اجرا با Docker
```bash
# ساخت و اجرای کانتینرها
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f
```

## مستندات

- [ویژگی دیتابیس گروه‌ها](DATABASE_GROUPS_FEATURE.md)
- [راهنمای سریع](QUICK_START.md)
- [ویژگی فیلتر پیام‌ها](MESSAGE_FILTERING.md)
- [ویژگی تشخیص لینک](LINK_DETECTION_FEATURE.md)

## مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. Branch جدید ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request ارسال کنید

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. 