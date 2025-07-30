# User JSON Processor - پردازشگر فایل‌های JSON کاربران

## 📋 خلاصه
این قابلیت جدید امکان ترکیب و پردازش فایل‌های JSON مربوط به کاربران را از Saved Messages فراهم می‌کند.

## 🚀 قابلیت‌ها

### ✅ **قابلیت‌های اصلی:**
- **پیدا کردن فایل‌های JSON:** جستجوی خودکار فایل‌های JSON مربوط به کاربر در Saved Messages
- **ترکیب هوشمند:** ترکیب تمام فایل‌های JSON یک کاربر در یک فایل نهایی
- **حذف تکرار:** جلوگیری از تکرار پیام‌ها و اطلاعات
- **ترکیب تاریخچه:** ترکیب هوشمند username_history و name_history از فایل‌های مختلف
- **پردازش مجدد:** اگر فایل نهایی وجود داشته باشد، فقط فایل‌های جدید را اضافه می‌کند
- **ذخیره در دیتابیس:** ذخیره اطلاعات فایل نهایی در MongoDB

### 🔧 **قابلیت‌های پیشرفته:**
- **شناسایی الگوهای مختلف:** پشتیبانی از فرمت‌های مختلف نام فایل
- **ترکیب اطلاعات گروه:** جمع‌آوری اطلاعات تمام گروه‌هایی که کاربر در آن‌ها عضو است
- **مرتب‌سازی زمانی:** مرتب کردن تاریخچه‌ها بر اساس زمان تغییر
- **لاگ کامل:** نمایش جزئیات کامل عملیات

## 📁 ساختار فایل‌ها

### فایل‌های اصلی:
```
analyzer/
├── services/
│   ├── user_json_manager.py      # مدیریت فایل‌های JSON کاربران
│   ├── mongo_service.py          # سرویس دیتابیس (به‌روزرسانی شده)
│   └── telegram_storage.py       # سرویس تلگرام (موجود)
├── user_json_processor.py        # اسکریپت اصلی پردازش
├── quick_user_process.py         # اسکریپت سریع پردازش
└── README_USER_JSON_PROCESSOR.md # این فایل
```

## 🛠️ نحوه استفاده

### 1. **پردازش یک کاربر:**
```bash
cd analyzer
python user_json_processor.py --user-id 123456789
```

### 2. **پردازش سریع:**
```bash
cd analyzer
python quick_user_process.py 123456789
```

### 3. **مشاهده لیست کاربران پردازش شده:**
```bash
cd analyzer
python user_json_processor.py --list
```

### 4. **مشاهده اطلاعات کاربر:**
```bash
cd analyzer
python user_json_processor.py --info 123456789
```

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
    "username_history": [
      {
        "username": "username1",
        "changed_at": "2025-07-28T09:56:13.772364+00:00"
      }
    ],
    "name_history": [
      {
        "name": "نام قدیمی",
        "changed_at": "2025-07-28T09:56:13.772361+00:00"
      },
      {
        "name": "نام جدید",
        "changed_at": "2025-07-30T22:27:21.967105+00:00"
      }
    ],
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
  "groups_info": [
    {
      "group_id": "-1001653610103",
      "group_title": "نام گروه",
      "group_username": "group_username",
      "joined_at": "2025-07-30T22:27:21.967159+00:00",
      "role": "member",
      "is_admin": false
    }
  ]
}
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
```

## 📈 آمار و گزارش‌ها

### لاگ‌های مهم:
- `✅ Found X JSON files for user Y`: تعداد فایل‌های پیدا شده
- `📋 Combined username history: X entries`: تعداد username های مختلف
- `📋 Combined name history: X entries`: تعداد name های مختلف
- `📊 Total unique messages: X`: تعداد پیام‌های منحصر به فرد
- `📊 Total groups found: X`: تعداد گروه‌های پیدا شده
- `✅ Final JSON sent: filename.json`: نام فایل نهایی ارسال شده

## 🔍 الگوهای شناسایی فایل

### فرمت‌های پشتیبانی شده:
1. `temp_user_id_group_id_timestamp_uuid.json`
2. `temp_user_id_-group_id_timestamp_uuid.json`
3. `user_id_group_id_timestamp_uuid.json`
4. `user_id_-group_id_timestamp_uuid.json`
5. `temp_user_id_*.json`
6. `user_id_*.json`

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

### نسخه 1.0 (2025-07-30):
- ✅ پیاده‌سازی اولیه
- ✅ ترکیب فایل‌های JSON
- ✅ حذف تکرار پیام‌ها
- ✅ ترکیب تاریخچه username و name
- ✅ ذخیره در MongoDB
- ✅ پشتیبانی از پردازش مجدد

---

**توسعه‌دهنده:** AI Assistant  
**تاریخ آخرین به‌روزرسانی:** 2025-07-30  
**نسخه:** 1.0 