# Telegram Analyzer - Complete Feature Set

## 🚀 Main Features

### 1. **Group Filtering & Processing** ⭐ NEW
- **Automatic chat type detection**: Groups, Supergroups, Channels, Private chats
- **Group-only user extraction**: Only process groups and supergroups for user data
- **Channel database storage**: Save channel information to MongoDB without user extraction
- **Comprehensive statistics**: Detailed reporting of processed vs skipped chats
- **Smart filtering**: Skip channels and other chat types while preserving information

### 2. **Message Analysis**
- Extract messages from Telegram groups and channels
- Analyze message content and metadata
- Track message reactions and forwards
- Process both text messages and media captions
- **🆕 Generate direct message links** for easy access to original messages

### 3. **Member Tracking**
- Extract detailed member information from groups only
- Track user activity and engagement
- Monitor username and name changes
- Identify bots and deleted accounts

### 4. **Link Detection & Extraction**
- Automatically detect links in messages
- Extract various link formats:
  - `https://t.me/channel_name`
  - `@username`
  - `t.me/username`
  - `https://t.me/joinchat/HASH`
  - Regular URLs
- Save extracted links to files
- Prevent duplicate links
- Generate comprehensive link reports

### 5. **URL Resolution**
- Resolve redirect links to find actual Telegram links
- Handle Google Translate and other redirect services
- Validate and categorize link types
- Track redirect chains

### 6. **MongoDB Integration** ⭐ NEW
- Store chat information in MongoDB database
- Track scan status and statistics
- Save both processed and skipped chat data
- Maintain comprehensive chat history

### 7. **Comprehensive Reporting**
- Generate detailed JSON reports
- Create user activity summaries
- Export data in multiple formats
- Provide statistical analysis
- **🆕 Enhanced statistics**: Processed groups, saved channels, failed attempts

### 8. **🆕 Message Links Feature**
- Generate direct links to individual messages
- Format: `https://t.me/username/message_id`
- Include links in user data exports
- Enable easy verification and navigation
- Support for all message types (text, media, etc.)

### 9. **Telegram Cloud Storage**
- Send user data files directly to Telegram
- Store files in Saved Messages or custom chat
- Automatic file naming and organization
- Cloud-based data management

## 📁 File Structure

```
analyzer/
├── main.py                          # Main application
├── links.txt                        # Input chat links
├── config/
│   └── settings.py                  # Configuration
├── services/
│   ├── telegram_client.py           # Telegram API client
│   ├── message_analyzer.py          # Message processing
│   ├── link_analyzer.py             # Link extraction
│   ├── user_tracker.py              # User tracking
│   ├── mongo_service.py             # MongoDB integration
│   └── file_manager.py              # File operations
├── models/
│   └── data_models.py               # Data structures
├── utils/
│   └── logger.py                    # Logging
└── results/                         # Output directory
    ├── extracted_links.txt          # Individual chat links
    ├── all_extracted_links.txt      # Combined links
    └── analysis_summary.json        # Analysis summary
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Telegram API Configuration
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string

# MongoDB Configuration (Optional)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=telegram_analyzer

# Telegram Storage Configuration (Optional)
TELEGRAM_STORAGE_MODE=saved_messages
TELEGRAM_STORAGE_CHAT_ID=your_chat_id

# Analysis Settings
MESSAGE_LIMIT=1000
GET_MEMBERS=true
MEMBER_LIMIT=5000
```

### Input File (links.txt)
```
https://t.me/example_group
@example_channel
+1234567890
https://t.me/joinchat/HASH
```

## 📊 Output Files

### Analysis Results
- `analysis_summary.json` - Main analysis summary
- `extracted_links.txt` - Individual chat links
- `all_extracted_links.txt` - Combined unique links

### Telegram Cloud Storage
- `{user_id}_{group_id}_{timestamp}_{unique_id}.json` - User data files
- `summary_{timestamp}_{unique_id}.json` - Summary files

### MongoDB Database
- Chat information for all processed and skipped chats
- Scan statistics and status tracking
- Comprehensive chat history

## 🎯 Processing Logic

### Chat Type Handling
- ✅ **Groups & Supergroups**: Full processing (messages + users + links)
- 📢 **Channels**: Database storage only (no user extraction)
- 📝 **Other chats**: Database storage only (no user extraction)

### Statistics Output
```
📊 Analysis Summary:
   ✅ Successfully processed: 5 groups
   📢 Channels saved to DB: 3
   📝 Other chats saved to DB: 1
   ⏭️ Total skipped: 4
   ❌ Failed: 1
   📋 Total links: 9
   🔗 Total extracted links: 45
   👤 Total users extracted: 800
   💬 Total messages processed: 2,300
```

## 🚀 Key Benefits

1. **Smart Filtering**: Only extract users from groups, save channel info
2. **Complete Database**: All chat information stored in MongoDB
3. **Message Links**: Direct access to original messages
4. **Cloud Storage**: Telegram-based file management
5. **Comprehensive Reporting**: Detailed statistics and analysis
6. **Error Handling**: Robust error handling and recovery
7. **Scalable**: Handles large numbers of chats efficiently 