# راهنمای سریع شروع

## 🚀 نصب و راه‌اندازی

### 1. تنظیم فایل .env
```bash
# در پوشه analyzer فایل .env ایجاد کنید
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string

# تنظیمات ذخیره‌سازی (اختیاری)
TELEGRAM_STORAGE_MODE=saved_messages
```

### 2. تنظیم فایل links.txt
```bash
# لینک‌های تلگرام را در links.txt قرار دهید
https://t.me/example_group
@example_channel
```

### 3. اجرای برنامه
```bash
python main.py
```

## 📁 خروجی‌ها

### فایل‌های محلی (results/)
- `analysis_[chat_id].json` - تحلیل تفصیلی هر چت
- `extracted_links.txt` - لینک‌های استخراج شده

### فایل‌های تلگرام (Saved Messages)
- `{user_id}_{group_id}_{timestamp}_{unique_id}.json` - داده‌های کاربران
- `summary_{timestamp}_{unique_id}.json` - فایل خلاصه

## ⚙️ تنظیمات پیشرفته

### استفاده از چت خاص
```bash
TELEGRAM_STORAGE_MODE=custom_chat
TELEGRAM_STORAGE_CHAT_ID=your_chat_id
```

### تنظیم محدودیت‌ها
```bash
MESSAGE_LIMIT=1000
GET_MEMBERS=true
MEMBER_LIMIT=5000
```

## 🔧 عیب‌یابی

### خطای PEER_ID_INVALID
- از Saved Messages استفاده کنید
- یا ابتدا عضو چت مورد نظر شوید

### خطای اتصال
- API_ID و API_HASH را بررسی کنید
- SESSION_STRING را بررسی کنید

## 📊 نمونه خروجی

```
🚀 Starting Telegram Chat Analyzer...
📋 Found 1 chat(s) to analyze
🔍 Analyzing chat: https://t.me/example_group
📝 Processing 150 messages...
👥 Processing 50 members...
✅ Telegram storage client started
✅ Sent user 123456789 in group -1001234567890 to Telegram
✅ Summary sent to Telegram
🎉 Export completed! Sent 25 files for 25 users in 1 groups to Telegram
✅ Analysis completed! Processed 1 chats
``` 