# Telegram Chat Analyzer

A comprehensive Telegram chat analysis tool that extracts messages, members, links, and user information from Telegram groups and channels. Now with **Group Filtering**, **Telegram Cloud Storage**, and **Message Links**!

## Features

- **Group-Only Processing**: Automatically filters and processes only groups/supergroups, skips channels
- **Channel Database Storage**: Saves channel information to database without user extraction
- **Message Analysis**: Extract and analyze messages from Telegram groups
- **Member Tracking**: Get detailed information about group members
- **Link Detection**: Automatically detect and extract links from messages
- **User Tracking**: Track user activity and engagement
- **Comprehensive Reports**: Generate detailed JSON reports
- **Link Storage**: Save extracted links to files for further processing
- **🆕 Telegram Cloud Storage**: Send user data files directly to Telegram instead of local storage
- **🆕 Message Links**: Generate direct links to individual messages in user data
- **🆕 MongoDB Integration**: Store chat information in MongoDB database

## How to use

### 1. Setup .env file
Create a `.env` file with your Telegram API credentials:

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
# TELEGRAM_STORAGE_CHAT_ID=your_chat_id
```

### 2. Setup links.txt
Add your Telegram chat links to `links.txt`:

```
https://t.me/example_group
@example_channel
```

**Note**: Only groups and supergroups will be processed for user extraction. Channels will be saved to database but users won't be extracted.

### 3. Run the program
```bash
python main.py
```

## Output

### Analysis Summary
The program provides detailed statistics:

```
📊 Analysis Summary:
   ✅ Successfully processed: 5 groups
   📢 Channels saved to DB: 3
   📝 Other chats saved to DB: 1
   ⏭️ Total skipped: 4
   ❌ Failed: 1
   📋 Total links: 9
```

### Local Files
The program generates the following files in the `results/` directory:

- `analysis_[chat_id].json` - Detailed analysis for each chat
- `analysis_summary.json` - Overall summary of all analyses
- `extracted_links.txt` - Links found in individual chat analysis
- `all_extracted_links.txt` - All unique links from all analyzed chats
- `extracted_links.json` - JSON format of extracted links

### Telegram Cloud Storage
User data files are sent directly to Telegram with the following naming format:

- `{user_id}_{group_id}_{timestamp}_{unique_id}.json` - Individual user data files
- `summary_{timestamp}_{unique_id}.json` - Summary files

**Example:**
```
1410974894_-1002548215273_20250727_191737_a1b2c3d4.json
summary_20250727_191740_m3n4o5p6.json
```

### Message Links Feature
Each message in user data now includes a direct link to the original message:

```json
{
  "messages_in_this_group": [
    {
      "message_id": 12345,
      "text": "Hello world!",
      "timestamp": "2024-01-15T10:30:00Z",
      "message_link": "https://t.me/example_channel/12345"
    }
  ]
}
```

**Benefits:**
- Direct access to original messages
- Easy verification of message content
- Quick navigation to specific messages
- Enhanced user data analysis capabilities

## Configuration

You can customize the analysis by modifying environment variables:

### Analysis Settings
- `MESSAGE_LIMIT` - Maximum number of messages to analyze (0 = unlimited)
- `GET_MEMBERS` - Whether to extract member information
- `MEMBER_LIMIT` - Maximum number of members to analyze (0 = unlimited)

### Telegram Storage Settings
- `TELEGRAM_STORAGE_MODE` - Storage mode: `saved_messages` (default) or `custom_chat`
- `TELEGRAM_STORAGE_CHAT_ID` - Target chat ID for custom storage mode

### MongoDB Settings
- `MONGO_URI` - MongoDB connection string
- `MONGO_DB_NAME` - Database name for storing chat information

## Group Filtering

The system automatically filters chat types:

- ✅ **Processed**: Groups and Supergroups (users extracted)
- 📢 **Saved to DB**: Channels (information saved, no user extraction)
- 📝 **Saved to DB**: Other chat types (information saved, no user extraction)

## Example output

```
🚀 Starting Telegram Chat Analyzer
============================================================
📋 Found 3 links to analyze
============================================================
🔍 Analysis 1/3: https://t.me/example_group
   ✅ Processing group: Example Group (Type: supergroup)
   📝 Retrieved 1500 messages
   👥 Retrieved 500 members
   🔗 Generated message links for all messages
✅ Analysis completed: https://t.me/example_group
   📄 Results saved to: results/analysis_-1001234567890.json
🔍 Analysis 2/3: @example_channel
   ⚠️ Skipping channel: Example Channel (ID: -1009876543210)
   📢 Channel type detected - only groups are processed
✅ Channel info saved to MongoDB: -1009876543210
🔍 Analysis 3/3: https://t.me/another_group
   ✅ Processing group: Another Group (Type: group)
   📝 Retrieved 800 messages
   👥 Retrieved 300 members
   🔗 Generated message links for all messages
✅ Analysis completed: https://t.me/another_group
   📄 Results saved to: results/analysis_-1001112223330.json
============================================================
📊 Final Summary:
   ✅ Successfully processed: 2 groups
   📢 Channels saved to DB: 1
   📝 Other chats saved to DB: 0
   ⏭️ Total skipped: 1
   ❌ Failed: 0
   📋 Total links: 3
   🔗 Total extracted links: 45
   👤 Total users extracted: 800
   💬 Total messages processed: 2,300
✅ Program completed successfully!
``` 