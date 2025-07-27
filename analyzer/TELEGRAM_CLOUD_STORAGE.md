# Telegram Cloud Storage Feature

## Overview
این ویژگی جدید امکان ارسال فایل‌های JSON کاربران به تلگرام را به عنوان کلاود استوریج فراهم می‌کند. به جای ذخیره فایل‌ها در سیستم محلی، فایل‌ها مستقیماً به چت تلگرام با ID `6682562049` ارسال می‌شوند.

## Features

### 🔄 تغییر از ذخیره محلی به تلگرام
- **قبل**: فایل‌ها در پوشه `users/` ذخیره می‌شدند
- **حالا**: فایل‌ها به تلگرام ارسال می‌شوند

### 📁 ساختار فایل‌های ارسالی
هر فایل JSON شامل:
- اطلاعات کامل کاربر
- تاریخچه نام و یوزرنیم
- پیام‌های کاربر در گروه خاص
- اطلاعات گروه
- متادیتای صادرات

### 📊 فایل خلاصه
یک فایل خلاصه شامل:
- آمار کلی کاربران
- اطلاعات گروه‌ها
- الگوی نام‌گذاری فایل‌ها

## Files Modified

### 1. `services/telegram_storage.py` (جدید)
کلاس `TelegramStorage` برای ارسال فایل‌ها به تلگرام:
- `send_json_file()`: ارسال فایل JSON
- `send_user_data()`: ارسال داده‌های کاربر
- `send_summary_file()`: ارسال فایل خلاصه

### 2. `services/user_tracker.py`
اضافه شدن متد جدید:
- `save_all_users_to_telegram()`: ارسال کاربران به تلگرام

### 3. `main.py` و `core/analyzer.py`
تغییر از `save_all_users()` به `save_all_users_to_telegram()`

## Usage

### اجرای عادی
```bash
python main.py
```

### تست عملکرد
```bash
python test_telegram_storage.py
```

## Configuration

### متغیرهای محیطی مورد نیاز
```bash
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
```

### تنظیم چت مقصد
در `services/telegram_storage.py`:
```python
def __init__(self, target_chat_id: int = 6682562049):
```

## File Naming Convention

### فایل‌های کاربر
```
{user_id}_{group_id}_{timestamp}_{unique_id}.json
```

**مثال:**
```
1410974894_-1002548215273_20250727_191737_a1b2c3d4.json
```

### فایل خلاصه
```
summary_{timestamp}_{unique_id}.json
```

**مثال:**
```
summary_20250727_191740_m3n4o5p6.json
```

## Caption Format

### فایل‌های کاربر
```
👤 User: {user_name} (@{username})
📊 Messages: {message_count}
📅 {timestamp}
```

### فایل خلاصه
```
📊 Analysis Summary
👥 Total Users: {total_users}
📝 Total Files: {total_files}
📅 {timestamp}
```

## Error Handling

### FloodWait
در صورت محدودیت تلگرام، سیستم منتظر می‌ماند و دوباره تلاش می‌کند.

### RPC Errors
خطاهای RPC ثبت و گزارش می‌شوند.

### Temporary Files
فایل‌های موقت پس از ارسال حذف می‌شوند.

## Benefits

### ✅ مزایا
- **امنیت**: فایل‌ها در تلگرام ذخیره می‌شوند
- **دسترسی**: امکان دسترسی از هر جا
- **پشتیبان**: تلگرام به عنوان بک‌آپ
- **اشتراک**: امکان اشتراک‌گذاری آسان

### ⚠️ محدودیت‌ها
- **اندازه فایل**: محدودیت 50MB تلگرام
- **نرخ ارسال**: محدودیت API تلگرام
- **وابستگی**: نیاز به اتصال اینترنت

## Troubleshooting

### خطاهای رایج

#### 1. خطای اتصال
```
❌ Failed to start Telegram storage client
```
**راه‌حل**: بررسی API_ID و API_HASH

#### 2. خطای ارسال
```
❌ RPC Error sending file
```
**راه‌حل**: بررسی محدودیت‌های تلگرام

#### 3. خطای چت
```
❌ Chat not found
```
**راه‌حل**: بررسی ID چت مقصد

## Future Enhancements

### 🔮 ویژگی‌های آینده
- پشتیبانی از چندین چت مقصد
- فشرده‌سازی فایل‌ها
- رمزگذاری فایل‌ها
- آرشیو خودکار
- گزارش‌گیری پیشرفته 