# 🚀 Quick Start - Docker

## 1. نصب Docker

### Windows
```bash
# دانلود و نصب Docker Desktop
# https://www.docker.com/products/docker-desktop/
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# یا استفاده از script رسمی
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## 2. راه‌اندازی سریع

### روش 1: استفاده از Makefile
```bash
# راه‌اندازی اولیه
make setup

# ویرایش فایل‌های تنظیمات
# 1. فایل .env را ویرایش کنید و API credentials را وارد کنید
# 2. فایل links.txt را ویرایش کنید و لینک‌های تلگرام را اضافه کنید

# اجرای container
make up-build
```

### روش 2: استفاده از Script
```bash
# Windows
setup-docker.bat

# Linux/Mac
./setup-docker.sh
```

### روش 3: دستی
```bash
# کپی کردن فایل نمونه
cp env.example .env

# ویرایش فایل‌ها
# 1. .env - API credentials
# 2. links.txt - لینک‌های تلگرام

# اجرای Docker
docker-compose up --build
```

## 3. تنظیم API Credentials

فایل `.env` را ویرایش کنید:

```env
API_ID=12345678
API_HASH=your_api_hash_here
SESSION_STRING=your_session_string_here
```

**نکته:** API credentials را از [https://my.telegram.org/apps](https://my.telegram.org/apps) دریافت کنید.

## 4. تنظیم لینک‌های تلگرام

فایل `links.txt` را ویرایش کنید:

```txt
https://t.me/example_channel
@example_group
+1234567890
```

## 5. اجرا

```bash
# اجرای کامل
docker-compose up

# اجرا در background
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f
```

## 6. نتایج

نتایج در پوشه `results/` ذخیره می‌شود:
- `my_chats.json` - نتایج کامل
- `extracted_links.txt` - لینک‌های استخراج شده

## 🔧 دستورات مفید

```bash
# توقف
docker-compose down

# Restart
docker-compose restart

# مشاهده وضعیت
docker-compose ps

# اجرای shell در container
docker-compose exec telegram-scanner bash

# مشاهده لاگ‌ها
docker-compose logs -f telegram-scanner
```

## 🆘 عیب‌یابی

### خطای API credentials
```
❌ Error: API_ID and API_HASH environment variables are required!
```
**راه حل:** فایل `.env` را بررسی کنید و API credentials صحیح را وارد کنید.

### خطای Docker
```
❌ Docker is not installed
```
**راه حل:** Docker Desktop را نصب کنید.

### خطای Rate Limit
```
FloodWait error
```
**راه حل:** صبر کنید و دوباره تلاش کنید.

## 📞 پشتیبانی

برای اطلاعات بیشتر:
- `DOCKER_README.md` - راهنمای کامل
- `make help` - دستورات مفید 