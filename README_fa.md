# 🔍 Telegram Scanner - اسکنر پیشرفته تلگرام

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> یک ابزار قدرتمند و جامع برای تحلیل، اسکن و پردازش اطلاعات گروه‌ها و کاربران تلگرام

## 📋 فهرست مطالب

- [🎯 ویژگی‌های کلیدی](#-ویژگی‌های-کلیدی)
- [🏗️ ساختار پروژه](#️-ساختار-پروژه)
- [🚀 راه‌اندازی سریع](#-راه‌اندازی-سریع)
- [📦 نصب و راه‌اندازی](#-نصب-و-راه‌اندازی)
- [🔧 تنظیمات](#-تنظیمات)
- [💻 نحوه استفاده](#-نحوه-استفاده)
- [📊 قابلیت‌های پیشرفته](#-قابلیت‌های-پیشرفته)
- [🐳 Docker](#-docker)
- [📚 مستندات](#-مستندات)
- [🤝 مشارکت](#-مشارکت)

## 🎯 ویژگی‌های کلیدی

### 🔍 **اسکنر اصلی**
- ✅ **اسکن گروه‌ها:** تحلیل کامل گروه‌ها و کانال‌های تلگرام
- ✅ **استخراج کاربران:** جمع‌آوری اطلاعات کامل کاربران
- ✅ **تحلیل پیام‌ها:** پردازش و تحلیل پیام‌های گروه
- ✅ **استخراج لینک‌ها:** شناسایی و اعتبارسنجی لینک‌ها
- ✅ **ردیابی واکنش‌ها:** تحلیل واکنش‌ها و فورواردها

### 🗄️ **مدیریت داده**
- ✅ **ذخیره در MongoDB:** ذخیره اطلاعات در دیتابیس
- ✅ **ارسال به Saved Messages:** ارسال نتایج به تلگرام
- ✅ **پشتیبان‌گیری خودکار:** مدیریت امن داده‌ها
- ✅ **گزارش‌گیری:** گزارش‌های جامع و تحلیلی

### 🔄 **پردازشگر JSON کاربران**
- ✅ **ترکیب هوشمند:** ترکیب فایل‌های JSON کاربران
- ✅ **ترکیب تاریخچه:** ترکیب username_history و name_history
- ✅ **حذف تکرار:** جلوگیری از تکرار پیام‌ها و اطلاعات
- ✅ **پردازش مجدد:** پشتیبانی از پردازش مجدد
- ✅ **ذخیره در دیتابیس:** ذخیره اطلاعات فایل نهایی

### 🤖 **اسکن هوشمند**
- ✅ **بررسی زمان:** جلوگیری از اسکن‌های غیرضروری
- ✅ **ادامه از آخرین پیام:** ادامه از آخرین پیام اسکن شده
- ✅ **نمایش پیشرفت:** نمایش زمان باقی‌مانده
- ✅ **مدیریت گروه‌ها:** خواندن گروه‌ها از دیتابیس

## 🏗️ ساختار پروژه

```
TelegramScaner/
├── 📁 analyzer/                    # پوشه اصلی برنامه
│   ├── 📁 config/                 # تنظیمات
│   ├── 📁 core/                   # هسته برنامه
│   ├── 📁 models/                 # مدل‌های داده
│   ├── 📁 services/               # سرویس‌های اصلی
│   │   ├── telegram_client.py     # کلاینت تلگرام
│   │   ├── telegram_storage.py    # ذخیره‌سازی تلگرام
│   │   ├── mongo_service.py       # سرویس MongoDB
│   │   ├── user_json_manager.py   # مدیریت JSON کاربران
│   │   └── ...                    # سایر سرویس‌ها
│   ├── 📁 utils/                  # ابزارها
│   ├── main.py                    # برنامه اصلی
│   ├── user_json_processor.py     # پردازشگر JSON کاربران
│   ├── quick_user_process.py      # پردازش سریع
│   └── README.md                  # مستندات analyzer
├── 📁 WebScraping/                # بخش وب‌اسکرپینگ
│   ├── browser_manager.py         # مدیریت مرورگر
│   ├── data_collector.py          # جمع‌آوری داده
│   ├── telegram_scraper.py        # اسکرپر تلگرام
│   └── ...                        # سایر فایل‌ها
├── 📁 testUserClientBot/          # بات تست کاربر
├── 📁 data/                       # داده‌ها
├── 📁 logs/                       # لاگ‌ها
├── 🐳 docker-compose.yml          # تنظیمات Docker
├── 🐳 Dockerfile                  # فایل Docker
├── 📄 env.example                 # نمونه تنظیمات
└── 📄 README.md                   # این فایل
```

## 🚀 راه‌اندازی سریع

### با Docker (پیشنهادی)
```bash
# 1. کلون کردن پروژه
git clone <repository-url>
cd TelegramScaner

# 2. تنظیم فایل محیط
cp env.example .env
# ویرایش فایل .env با اطلاعات خود

# 3. راه‌اندازی با Docker
docker-compose up -d

# 4. اجرای اسکنر
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python main.py"
```

### بدون Docker
```bash
# 1. نصب وابستگی‌ها
pip install -r requirements.txt

# 2. تنظیم فایل محیط
cp env.example .env
# ویرایش فایل .env

# 3. اجرای برنامه
python analyzer/main.py
```

## 📦 نصب و راه‌اندازی

### پیش‌نیازها
- **Python 3.8+**
- **MongoDB** (یا Docker)
- **Docker** (اختیاری)
- **API تلگرام** (API_ID و API_HASH)

### نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### تنظیم API تلگرام
1. به [my.telegram.org](https://my.telegram.org) بروید
2. وارد شوید و یک اپلیکیشن جدید ایجاد کنید
3. `API_ID` و `API_HASH` را کپی کنید
4. در فایل `.env` قرار دهید

## 🔧 تنظیمات

### فایل `.env`
```bash
# تنظیمات تلگرام
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string

# تنظیمات MongoDB
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups

# تنظیمات ذخیره‌سازی
TELEGRAM_STORAGE_MODE=saved_messages

# تنظیمات اسکن
MESSAGE_LIMIT=0
MEMBER_LIMIT=0
DEEP_SCAN=true
USE_DATABASE_FOR_GROUPS=true
SCAN_INTERVAL_MINUTES=30
```

### تنظیمات پیشرفته
```bash
# تنظیمات پیام‌ها
MESSAGE_BATCH_SIZE=200
DELAY_BETWEEN_BATCHES=0

# تنظیمات اعضا
MEMBER_BATCH_SIZE=500
GET_MEMBERS=true
INCLUDE_BOTS=true

# تنظیمات تحلیل
EXTRACT_ALL_MESSAGES=true
EXTRACT_ALL_MEMBERS=true
EXTRACT_MEDIA_INFO=true
EXTRACT_REACTIONS=true
SAVE_MESSAGE_TEXT=true
ANALYZE_MEDIA=true
TRACK_REACTIONS=true
TRACK_FORWARDS=true
```

## 💻 نحوه استفاده

### 1. اسکن گروه‌ها
```bash
# اجرای اسکنر اصلی
python analyzer/main.py

# یا با Docker
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python main.py"
```

### 2. پردازش فایل‌های JSON کاربران
```bash
# پردازش یک کاربر
python analyzer/user_json_processor.py --user-id 123456789

# پردازش سریع
python analyzer/quick_user_process.py 123456789

# مشاهده لیست کاربران پردازش شده
python analyzer/user_json_processor.py --list
```

### 3. انتقال گروه‌ها به دیتابیس
```bash
# انتقال گروه‌ها از فایل به دیتابیس
python analyzer/migrate_groups_to_db.py
```

### 4. وب‌اسکرپینگ
```bash
# اجرای وب‌اسکرپر
python WebScraping/main.py
```

## 📊 قابلیت‌های پیشرفته

### 🔍 **اسکن هوشمند**
- بررسی زمان آخرین اسکن
- ادامه از آخرین پیام اسکن شده
- نمایش زمان باقی‌مانده
- مدیریت گروه‌ها از دیتابیس

### 📊 **تحلیل پیشرفته**
- تحلیل پیام‌ها و محتوا
- استخراج لینک‌ها و اعتبارسنجی
- ردیابی واکنش‌ها و فورواردها
- تحلیل رسانه‌ها و فایل‌ها

### 🗄️ **مدیریت داده**
- ذخیره در MongoDB
- پشتیبان‌گیری خودکار
- گزارش‌گیری جامع
- ارسال به Saved Messages

### 🔄 **پردازشگر JSON**
- ترکیب هوشمند فایل‌ها
- ترکیب تاریخچه username و name
- حذف تکرار پیام‌ها
- پردازش مجدد با فایل‌های جدید

## 🐳 Docker

### راه‌اندازی با Docker
```bash
# ساخت و اجرای کانتینرها
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f

# توقف سرویس‌ها
docker-compose down
```

### تنظیمات Docker
```yaml
# docker-compose.yml
version: '3.8'
services:
  telegram-scanner:
    build: .
    environment:
      - API_ID=${API_ID}
      - API_HASH=${API_HASH}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - mongodb
  
  mongodb:
    image: mongo:latest
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db
```

## 📚 مستندات

### 📖 مستندات اصلی
- [README_FINAL.md](README_FINAL.md) - مستندات کامل پروژه
- [analyzer/README.md](analyzer/README.md) - مستندات analyzer
- [DOCKER_README.md](DOCKER_README.md) - راهنمای Docker

### 📋 ویژگی‌های خاص
- [analyzer/DATABASE_GROUPS_FEATURE.md](analyzer/DATABASE_GROUPS_FEATURE.md) - ویژگی دیتابیس گروه‌ها
- [analyzer/QUICK_START.md](analyzer/QUICK_START.md) - راهنمای سریع
- [analyzer/MESSAGE_FILTERING.md](analyzer/MESSAGE_FILTERING.md) - فیلتر پیام‌ها
- [analyzer/LINK_DETECTION_FEATURE.md](analyzer/LINK_DETECTION_FEATURE.md) - تشخیص لینک
- [analyzer/README_USER_JSON_PROCESSOR.md](analyzer/README_USER_JSON_PROCESSOR.md) - پردازشگر JSON

### 🚀 راهنماهای سریع
- [QUICK_START_DOCKER.md](QUICK_START_DOCKER.md) - راهنمای سریع Docker
- [analyzer/QUICK_START_FINAL.md](analyzer/QUICK_START_FINAL.md) - راهنمای نهایی
- [analyzer/QUICK_START_SMART_SCANNING.md](analyzer/QUICK_START_SMART_SCANNING.md) - اسکن هوشمند

## 🤝 مشارکت

برای مشارکت در پروژه:

1. **Fork** کنید
2. **Branch** جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
3. تغییرات را **commit** کنید (`git commit -m 'Add amazing feature'`)
4. **Push** کنید (`git push origin feature/amazing-feature`)
5. **Pull Request** ارسال کنید

### 🐛 گزارش باگ
اگر باگی پیدا کردید، لطفاً:
1. مشکل را در [Issues](https://github.com/your-repo/issues) گزارش دهید
2. جزئیات کامل مشکل را ارائه دهید
3. لاگ‌های مربوطه را ضمیمه کنید

## 📄 لایسنس

این پروژه تحت لایسنس **MIT** منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

## 🙏 تشکر

- **Telegram API** برای ارائه API قدرتمند
- **MongoDB** برای دیتابیس عالی
- **Python Community** برای ابزارهای عالی
- **Docker** برای containerization

---

**توسعه‌دهنده:** AI Assistant  
**تاریخ آخرین به‌روزرسانی:** 2025-01-27  
**نسخه:** 2.0  

⭐ اگر این پروژه برایتان مفید بود، لطفاً ستاره بدهید! 