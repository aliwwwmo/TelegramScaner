# Telegram Scanner - اسکنر تلگرام

## 📋 خلاصه پروژه
پروژه کامل اسکنر تلگرام با قابلیت‌های پیشرفته برای تحلیل و پردازش اطلاعات کاربران و گروه‌ها.

## 🚀 قابلیت‌های اصلی

### ✅ **اسکنر اصلی:**
- **اسکن گروه‌ها:** تحلیل کامل گروه‌های تلگرام
- **استخراج اطلاعات کاربران:** جمع‌آوری اطلاعات کامل کاربران
- **تحلیل پیام‌ها:** پردازش و تحلیل پیام‌های گروه
- **ذخیره در MongoDB:** ذخیره اطلاعات در دیتابیس
- **ارسال به Saved Messages:** ارسال نتایج به Saved Messages

### ✅ **User JSON Processor (جدید):**
- **ترکیب فایل‌های JSON:** ترکیب هوشمند فایل‌های JSON کاربران
- **ترکیب تاریخچه:** ترکیب username_history و name_history
- **حذف تکرار:** جلوگیری از تکرار پیام‌ها و اطلاعات
- **پردازش مجدد:** پشتیبانی از پردازش مجدد با فایل‌های جدید
- **ذخیره در دیتابیس:** ذخیره اطلاعات فایل نهایی

## 📁 ساختار پروژه

```
TelegramScaner/
├── analyzer/                    # پوشه اصلی برنامه
│   ├── services/               # سرویس‌های اصلی
│   │   ├── telegram_client.py
│   │   ├── telegram_storage.py
│   │   ├── mongo_service.py
│   │   ├── user_json_manager.py    # جدید
│   │   └── ...
│   ├── user_json_processor.py      # جدید - پردازشگر اصلی
│   ├── quick_user_process.py       # جدید - پردازش سریع
│   ├── main.py                     # برنامه اصلی
│   └── README_USER_JSON_PROCESSOR.md # مستندات جدید
├── docker-compose.yml
├── Dockerfile
├── env.example
└── README_FINAL.md              # این فایل
```

## 🛠️ نحوه استفاده

### 1. **راه‌اندازی با Docker:**
```bash
# کلون کردن پروژه
git clone <repository-url>
cd TelegramScaner

# تنظیم فایل env.example
cp env.example .env
# ویرایش فایل .env با اطلاعات خود

# راه‌اندازی با Docker
docker-compose up -d
```

### 2. **اسکن گروه‌ها:**
```bash
# اجرای اسکنر اصلی
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python main.py"
```

### 3. **پردازش فایل‌های JSON کاربران:**
```bash
# پردازش یک کاربر
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python user_json_processor.py --user-id 123456789"

# پردازش سریع
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python quick_user_process.py 123456789"

# مشاهده لیست کاربران پردازش شده
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python user_json_processor.py --list"
```

## 🔧 تنظیمات محیط

### متغیرهای محیطی مورد نیاز:
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
```

## 📊 قابلیت‌های جدید (User JSON Processor)

### ✅ **ویژگی‌های کلیدی:**
1. **شناسایی هوشمند فایل‌ها:** پشتیبانی از فرمت‌های مختلف نام فایل
2. **ترکیب تاریخچه:** ترکیب username_history و name_history از فایل‌های مختلف
3. **حذف تکرار:** جلوگیری از تکرار پیام‌ها و اطلاعات
4. **پردازش مجدد:** اگر فایل نهایی وجود داشته باشد، فقط فایل‌های جدید را اضافه می‌کند
5. **ذخیره در دیتابیس:** ذخیره اطلاعات فایل نهایی در MongoDB

### 📈 **آمار و گزارش‌ها:**
- تعداد فایل‌های پردازش شده
- تعداد پیام‌های منحصر به فرد
- تعداد گروه‌های پیدا شده
- تعداد username و name های مختلف

## 🔍 الگوهای شناسایی فایل

### فرمت‌های پشتیبانی شده:
1. `temp_user_id_group_id_timestamp_uuid.json`
2. `temp_user_id_-group_id_timestamp_uuid.json`
3. `user_id_group_id_timestamp_uuid.json`
4. `user_id_-group_id_timestamp_uuid.json`
5. `temp_user_id_*.json`
6. `user_id_*.json`

## 📊 ساختار خروجی

### فایل JSON نهایی شامل:
```json
{
  "user_id": 123456789,
  "merge_date": "2025-07-30T23:24:28.4577a40f",
  "total_files_merged": 9,
  "messages": [...],
  "user_info": {
    "current_username": "username",
    "current_name": "نام کاربر",
    "username_history": [...],
    "name_history": [...],
    "is_bot": false,
    "is_deleted": false,
    "is_verified": false,
    "is_premium": false,
    "is_scam": false,
    "is_fake": false,
    "phone_number": null,
    "language_code": null,
    "dc_id": 4,
    "first_seen": "2025-07-30T22:27:21.967095+00:00",
    "last_seen": "2025-07-30T22:27:21.970025+00:00"
  },
  "groups_info": [...]
}
```

## ⚠️ نکات مهم

### محدودیت‌ها:
- حداکثر 1000 پیام از Saved Messages بررسی می‌شود
- فایل‌های بزرگ ممکن است زمان بیشتری نیاز داشته باشند
- اتصال اینترنت پایدار برای دانلود فایل‌ها ضروری است

### بهترین شیوه‌ها:
- قبل از پردازش، اطمینان حاصل کنید که فایل‌های JSON در Saved Messages موجود هستند
- برای کاربران با فایل‌های زیاد، صبر کنید تا عملیات کامل شود
- از لاگ‌ها برای بررسی وضعیت پردازش استفاده کنید

## 🐛 عیب‌یابی

### مشکلات رایج:
1. **فایل‌ها پیدا نمی‌شوند:** بررسی کنید که فایل‌ها در Saved Messages موجود هستند
2. **خطای اتصال:** بررسی تنظیمات API و SESSION_STRING
3. **خطای دیتابیس:** بررسی اتصال MongoDB

### راه‌حل‌ها:
- از `--list` برای بررسی کاربران پردازش شده استفاده کنید
- لاگ‌ها را بررسی کنید تا مشکل را شناسایی کنید
- تنظیمات محیط را دوباره بررسی کنید

## 📝 تاریخچه تغییرات

### نسخه 2.0 (2025-07-30):
- ✅ اضافه شدن User JSON Processor
- ✅ ترکیب هوشمند فایل‌های JSON
- ✅ ترکیب تاریخچه username و name
- ✅ حذف تکرار پیام‌ها و اطلاعات
- ✅ پشتیبانی از پردازش مجدد
- ✅ ذخیره در MongoDB
- ✅ مستندات کامل

### نسخه 1.0 (قبل از 2025-07-30):
- ✅ اسکنر اصلی تلگرام
- ✅ تحلیل گروه‌ها و کاربران
- ✅ ذخیره در MongoDB
- ✅ ارسال به Saved Messages

---

