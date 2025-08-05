# Telegram Scanner - راهنمای Docker

این پروژه تلگرام اسکنر حالا با Docker قابل اجرا است!

## 🚀 راهنمای سریع

### 1. نصب Docker و Docker Compose

ابتدا Docker و Docker Compose را نصب کنید:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- یا [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)

### 2. تنظیم API Credentials

فایل `.env` را ایجاد کنید:

```bash
cp env.example .env
```

سپس فایل `.env` را ویرایش کنید و API credentials تلگرام را وارد کنید:

```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

**نکته:** API credentials را از [https://my.telegram.org/apps](https://my.telegram.org/apps) دریافت کنید.

### 3. تنظیم لینک‌های تلگرام

فایل `links.txt` را ویرایش کنید و لینک‌های تلگرام را اضافه کنید:

```txt
https://t.me/example_channel
@example_group
+1234567890
```

### 4. اجرای Docker Container

```bash
# Build و اجرای container
docker-compose up --build

# یا اجرا در background
docker-compose up -d --build
```

## 📁 ساختار فایل‌ها

```
TelegramScaner/
├── analyzer/           # کد اصلی تحلیلگر
├── WebScraping/       # کامپوننت web scraping
├── testUserClientBot/ # کلاینت تست
├── results/           # نتایج تحلیل (mounted volume)
├── users/             # اطلاعات کاربران (mounted volume)
├── logs/              # فایل‌های لاگ (mounted volume)
├── data/              # داده‌های اضافی (mounted volume)
├── links.txt          # لینک‌های تلگرام
├── .env               # تنظیمات محیطی
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── requirements.txt   # Python dependencies
```

## ⚙️ تنظیمات پیشرفته

### Environment Variables

| متغیر | پیش‌فرض | توضیح |
|-------|----------|-------|
| `API_ID` | - | API ID تلگرام (ضروری) |
| `API_HASH` | - | API Hash تلگرام (ضروری) |
| `SESSION_STRING` | - | Session string برای login سریع |
| `MESSAGE_LIMIT` | 1000 | حداکثر تعداد پیام‌ها |
| `MEMBER_LIMIT` | 5000 | حداکثر تعداد اعضا |
| `GET_MEMBERS` | true | دریافت اطلاعات اعضا |
| `INCLUDE_BOTS` | true | شامل کردن bot ها |

### تنظیمات فایل‌ها

| متغیر | پیش‌فرض | توضیح |
|-------|----------|-------|
| `RESULTS_DIR` | /app/results | پوشه نتایج |
| `USERS_DIR` | /app/users | پوشه اطلاعات کاربران |
| `LOGS_DIR` | /app/logs | پوشه لاگ‌ها |
| `LINKS_FILE` | /app/links.txt | فایل لینک‌ها |

## 🔧 دستورات مفید

### اجرای تحلیل
```bash
# اجرای کامل
docker-compose up

# اجرا در background
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f
```

### مدیریت Container
```bash
# توقف
docker-compose down

# توقف و حذف volumes
docker-compose down -v

# rebuild
docker-compose up --build

# اجرای shell در container
docker-compose exec telegram-scanner bash
```

### اجرای دستی
```bash
# اجرای تحلیلگر
docker run --rm -v $(pwd)/results:/app/results -v $(pwd)/links.txt:/app/links.txt -e API_ID=your_id -e API_HASH=your_hash telegram-scanner

# اجرای web scraper
docker run --rm -v $(pwd)/data:/app/data telegram-scanner python WebScraping/main.py
```

## 📊 نتایج

نتایج تحلیل در پوشه `results/` ذخیره می‌شود:

- `my_chats.json` - نتایج کامل تحلیل
- `extracted_links.txt` - لینک‌های استخراج شده
- `all_extracted_links.txt` - تمام لینک‌های منحصر به فرد

## 🔍 عیب‌یابی

### خطاهای رایج

1. **API credentials نامعتبر**
   ```
   ❌ Error: API_ID and API_HASH environment variables are required!
   ```
   - API credentials را در فایل `.env` بررسی کنید
   - از [https://my.telegram.org/apps](https://my.telegram.org/apps) دریافت کنید

2. **خطای Chrome/Selenium**
   ```
   ChromeDriver error
   ```
   - Docker image شامل Chrome است
   - اگر مشکل ادامه دارد، container را rebuild کنید

3. **خطای Rate Limit**
   ```
   FloodWait error
   ```
   - تلگرام rate limit اعمال کرده
   - صبر کنید و دوباره تلاش کنید

### لاگ‌ها

```bash
# مشاهده لاگ‌های container
docker-compose logs telegram-scanner

# مشاهده لاگ‌های real-time
docker-compose logs -f telegram-scanner

# مشاهده لاگ‌های فایل
tail -f logs/telegram_analysis.log
```

## 🗄️ Database (اختیاری)

برای استفاده از MongoDB:

```bash
# اجرا با database
docker-compose --profile database up

# یا فقط database
docker-compose --profile database up mongodb
```

## 🔒 امنیت

- Container با کاربر غیر-root اجرا می‌شود
- فایل‌های حساس در volumes جداگانه ذخیره می‌شوند
- API credentials در environment variables محافظت می‌شوند

## 📈 Performance

### تنظیمات پیشنهادی

```env
# برای تحلیل سریع
MESSAGE_LIMIT=500
MEMBER_LIMIT=1000
DELAY_BETWEEN_BATCHES=2

# برای تحلیل کامل
MESSAGE_LIMIT=5000
MEMBER_LIMIT=10000
DELAY_BETWEEN_BATCHES=1
```

### Resource Limits

Container با محدودیت منابع اجرا می‌شود:
- Memory: 2GB max, 512MB reserved
- CPU: 1 core max, 0.5 core reserved

## 🤝 مشارکت

برای بهبود Docker setup:

1. Fork کنید
2. Feature branch ایجاد کنید
3. تغییرات را commit کنید
4. Pull request ارسال کنید

## 📞 پشتیبانی

اگر مشکلی دارید:
1. لاگ‌ها را بررسی کنید
2. این README را مطالعه کنید
3. Issue در GitHub ایجاد کنید 