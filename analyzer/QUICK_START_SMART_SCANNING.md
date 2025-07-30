# راهنمای سریع اسکن هوشمند

## 🚀 شروع سریع

### 1. تنظیم فایل .env
```bash
# تنظیمات اسکن هوشمند
SCAN_INTERVAL_MINUTES=30
RESUME_FROM_LAST_MESSAGE=true
SHOW_REMAINING_TIME=true
```

### 2. اجرای برنامه
```bash
cd analyzer
python main.py
```

## 📊 مثال خروجی

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

### آمار نهایی
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

## ⚙️ تنظیمات پیشرفته

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

## 🎯 مزایا

1. **بهینه‌سازی منابع**: جلوگیری از اسکن‌های غیرضروری
2. **ادامه هوشمند**: ادامه از آخرین پیام اسکن شده
3. **قابلیت تنظیم**: فاصله زمانی قابل تنظیم
4. **نمایش وضعیت**: نمایش زمان باقی‌مانده
5. **آمار دقیق**: گزارش کامل از انواع مختلف رد شدن

## 📝 نکات مهم

- **اولویت زمانی**: اگر گروه اخیراً اسکن شده، رد می‌شود
- **ادامه هوشمند**: از پیام بعدی آخرین پیام شروع می‌شود
- **نمایش وضعیت**: زمان باقی‌مانده نمایش داده می‌شود
- **آمار دقیق**: انواع مختلف رد شدن شمارش می‌شود
- **قابلیت تنظیم**: تمام پارامترها قابل تنظیم هستند 