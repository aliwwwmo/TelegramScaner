# ویژگی اسکن هوشمند

## خلاصه

این ویژگی جدید امکان اسکن هوشمند گروه‌ها را فراهم می‌کند که بر اساس زمان آخرین اسکن تصمیم می‌گیرد آیا گروه دوباره اسکن شود یا نه.

## تنظیمات جدید

### متغیرهای محیطی
```bash
# تنظیمات اسکن هوشمند
SCAN_INTERVAL_MINUTES=30
RESUME_FROM_LAST_MESSAGE=true
SHOW_REMAINING_TIME=true
```

### توضیح تنظیمات
- `SCAN_INTERVAL_MINUTES`: فاصله زمانی بین اسکن‌ها (دقیقه)
- `RESUME_FROM_LAST_MESSAGE`: ادامه از آخرین پیام اسکن شده
- `SHOW_REMAINING_TIME`: نمایش زمان باقی‌مانده تا اسکن بعدی

## نحوه کارکرد

### 1. بررسی زمان اسکن
برنامه قبل از اسکن هر گروه، زمان آخرین اسکن را بررسی می‌کند:

```
🔍 Checking group: @example_group
⏰ Last scan: 2024-01-15 10:30:00 (25 minutes ago)
⏭️ Skipping scan - too recent (wait 5 more minutes)
```

### 2. ادامه از آخرین پیام
اگر اسکن جدید انجام شود، از پیام بعدی آخرین پیام اسکن شده شروع می‌کند:

```
🔄 Resuming scan from message ID: 12345
📝 Filtered to 50 messages from ID 12345
```

### 3. نمایش زمان باقی‌مانده
برنامه زمان باقی‌مانده تا اسکن بعدی را نمایش می‌دهد:

```
⏰ Last scan: 2024-01-15 10:30:00 (25 minutes ago)
⏭️ Skipping scan - too recent (wait 5 دقیقه more)
```

## مثال خروجی

### گروهی که اخیراً اسکن شده
```
🔍 Starting analysis for: https://t.me/example_group
⏰ Last scan: 2024-01-15 10:30:00 (25 minutes ago)
⏭️ Skipping scan - too recent (wait 5 دقیقه more)
```

### گروهی که آماده اسکن است
```
🔍 Starting analysis for: https://t.me/another_group
✅ Group ready for scan (last scan: 2024-01-15 09:00:00)
🔄 Resuming scan from message ID: 12345
📝 Processing 50 messages...
```

### گروهی که برای اولین بار اسکن می‌شود
```
🔍 Starting analysis for: https://t.me/new_group
✅ Group ready for scan (last scan: Never)
📝 Processing 100 messages...
```

## آمار نهایی

برنامه آمار کاملی از اسکن‌ها ارائه می‌دهد:

```
📊 Analysis Summary:
   ✅ Successfully processed: 3 groups
   📢 Channels saved to DB: 1
   📝 Other chats saved to DB: 0
   ⏰ Too recent to scan: 2
   ⏭️ Total skipped: 3
   ❌ Failed: 0
   📋 Total links: 6
```

## مزایا

1. **بهینه‌سازی منابع**: جلوگیری از اسکن‌های غیرضروری
2. **ادامه هوشمند**: ادامه از آخرین پیام اسکن شده
3. **قابلیت تنظیم**: فاصله زمانی قابل تنظیم
4. **نمایش وضعیت**: نمایش زمان باقی‌مانده
5. **آمار دقیق**: گزارش کامل از انواع مختلف رد شدن

## تنظیمات پیشرفته

### تغییر فاصله زمانی
```bash
# اسکن هر 15 دقیقه
SCAN_INTERVAL_MINUTES=15

# اسکن هر 2 ساعت
SCAN_INTERVAL_MINUTES=120
```

### غیرفعال‌سازی ادامه از آخرین پیام
```bash
RESUME_FROM_LAST_MESSAGE=false
```

### غیرفعال‌سازی نمایش زمان باقی‌مانده
```bash
SHOW_REMAINING_TIME=false
```

## ساختار داده

اطلاعات اسکن در دیتابیس ذخیره می‌شود:

```json
{
  "chat_id": -1001234567890,
  "username": "example_group",
  "link": "https://t.me/example_group",
  "last_scan_time": "2024-01-15T10:30:00Z",
  "last_message_id": 12345,
  "start_message_id": 12300,
  "last_scan_status": "success",
  "scan_count": 5
}
```

## نکات مهم

1. **اولویت زمانی**: اگر گروه اخیراً اسکن شده، رد می‌شود
2. **ادامه هوشمند**: از پیام بعدی آخرین پیام شروع می‌شود
3. **نمایش وضعیت**: زمان باقی‌مانده نمایش داده می‌شود
4. **آمار دقیق**: انواع مختلف رد شدن شمارش می‌شود
5. **قابلیت تنظیم**: تمام پارامترها قابل تنظیم هستند 