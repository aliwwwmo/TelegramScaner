# Quick Start Guide

## 🚀 Installation and Setup

### 1. Configure .env file
```bash
# Create .env file in the analyzer folder
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string

# MongoDB settings (optional)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=telegram_analyzer

# Storage settings (optional)
TELEGRAM_STORAGE_MODE=saved_messages
```

### 2. Configure links.txt file
```bash
# Add Telegram links to links.txt
https://t.me/example_group
@example_channel
```

**Note**: Only groups and supergroups are processed. Channels are saved to the database but users are not extracted from them.

### 3. Run the application
```bash
python main.py
```

## 📁 Outputs

### Local files (results/)
- `analysis_[chat_id].json` - Detailed analysis of each chat
- `extracted_links.txt` - Extracted links
- `all_extracted_links.txt` - All unique links

### Telegram files (Saved Messages)
- `{user_id}_{group_id}_{timestamp}_{unique_id}.json` - User data
- `summary_{timestamp}_{unique_id}.json` - Summary file

### MongoDB Database
- Information of all chats (groups, channels, supergroups)
- Scan statistics and processing status

## ⚙️ Advanced Settings

### Using specific chat
```bash
TELEGRAM_STORAGE_MODE=custom_chat
TELEGRAM_STORAGE_CHAT_ID=your_chat_id
```

### Setting limits
```bash
MESSAGE_LIMIT=1000
GET_MEMBERS=true
MEMBER_LIMIT=5000
```

### MongoDB settings
```bash
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=telegram_analyzer
```

## 🔧 Troubleshooting

### PEER_ID_INVALID error
- Use Saved Messages
- Or join the target chat first

### Connection error
- Check API_ID and API_HASH
- Check SESSION_STRING

### MongoDB error
- Ensure MongoDB is installed and running
- Check MONGO_URI settings

## 📊 Sample Output

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

## 🎯 Key Features

- ✅ **Group filtering**: Only groups and supergroups are processed
- 📢 **Channel storage**: Channel information is saved to database
- 🔗 **Message links**: Direct links to original messages
- 💾 **Cloud storage**: Sending files to Telegram
- 📊 **Detailed reporting**: Complete statistics of processed and skipped items 