# راهنمای سریع شروع

## 🚀 نصب و راه‌اندازی

### 1. تنظیم فایل .env
```bash
# در پوشه analyzer فایل .env ایجاد کنید
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string

# تنظیمات MongoDB (اختیاری)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=telegram_analyzer

# تنظیمات ذخیره‌سازی (اختیاری)
TELEGRAM_STORAGE_MODE=saved_messages
```

### 2. تنظیم فایل links.txt
```bash
# لینک‌های تلگرام را در links.txt قرار دهید
https://t.me/example_group
@example_channel
```

**نکته**: فقط گروه‌ها و سوپرگروه‌ها پردازش می‌شوند. کانال‌ها در دیتابیس ذخیره می‌شوند اما کاربران از آنها استخراج نمی‌شود.

### 3. اجرای برنامه
```bash
python main.py
```

## 📁 خروجی‌ها

### فایل‌های محلی (results/)
- `analysis_[chat_id].json` - تحلیل تفصیلی هر چت
- `extracted_links.txt` - لینک‌های استخراج شده
- `all_extracted_links.txt` - تمام لینک‌های منحصر به فرد

### فایل‌های تلگرام (Saved Messages)
- `{user_id}_{group_id}_{timestamp}_{unique_id}.json` - داده‌های کاربران
- `summary_{timestamp}_{unique_id}.json` - فایل خلاصه

### دیتابیس MongoDB
- اطلاعات تمام چت‌ها (گروه‌ها، کانال‌ها، سوپرگروه‌ها)
- آمار اسکن و وضعیت پردازش

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

### تنظیمات MongoDB
```bash
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=telegram_analyzer
```

## 🔧 عیب‌یابی

### خطای PEER_ID_INVALID
- از Saved Messages استفاده کنید
- یا ابتدا عضو چت مورد نظر شوید

### خطای اتصال
- API_ID و API_HASH را بررسی کنید
- SESSION_STRING را بررسی کنید

### خطای MongoDB
- اطمینان از نصب و اجرای MongoDB
- بررسی تنظیمات MONGO_URI

## 📊 نمونه خروجی

```
🚀 Starting Telegram Chat Analyzer...
📋 Found 3 chat(s) to analyze
🔍 Analyzing chat 1/3: https://t.me/example_group
   ✅ Processing group: Example Group (Type: supergroup)
   📝 Processing 150 messages...
   👥 Processing 50 members...
   ✅ Group info saved to MongoDB: -1001234567890
🔍 Analyzing chat 2/3: @example_channel
   ⚠️ Skipping channel: Example Channel (ID: -1009876543210)
   📢 Channel type detected - only groups are processed
   ✅ Channel info saved to MongoDB: -1009876543210
🔍 Analyzing chat 3/3: https://t.me/another_group
   ✅ Processing group: Another Group (Type: group)
   📝 Processing 100 messages...
   👥 Processing 30 members...
   ✅ Group info saved to MongoDB: -1001112223330
📊 Analysis Summary:
   ✅ Successfully processed: 2 groups
   📢 Channels saved to DB: 1
   📝 Other chats saved to DB: 0
   ⏭️ Total skipped: 1
   ❌ Failed: 0
   📋 Total links: 3
   🔗 Total extracted links: 45
   👤 Total users extracted: 80
   💬 Total messages processed: 250
✅ Analysis completed!
```

## 🎯 ویژگی‌های کلیدی

- ✅ **فیلتر گروه‌ها**: فقط گروه‌ها و سوپرگروه‌ها پردازش می‌شوند
- 📢 **ذخیره کانال‌ها**: اطلاعات کانال‌ها در دیتابیس ذخیره می‌شود
- 🔗 **لینک پیام‌ها**: لینک مستقیم به پیام‌های اصلی
- 💾 **ذخیره ابری**: ارسال فایل‌ها به تلگرام
- 📊 **گزارش دقیق**: آمار کامل از پردازش شده‌ها و رد شده‌ها 