# Telegram Chat Analyzer

A comprehensive Telegram chat analysis tool that extracts messages, members, links, and user information from Telegram groups and channels.

## Features

- **Message Analysis**: Extract and analyze messages from Telegram chats
- **Member Tracking**: Get detailed information about chat members
- **Link Detection**: Automatically detect and extract links from messages
- **User Tracking**: Track user activity and engagement
- **Comprehensive Reports**: Generate detailed JSON reports
- **Link Storage**: Save extracted links to files for further processing

## How to use

### 1. Setup .env file
Create a `.env` file with your Telegram API credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
```

### 2. Setup links.txt
Add your Telegram chat links to `links.txt`:

```
https://t.me/example_group
@example_channel
```

### 3. Run the program
```bash
python main.py
```

## Output

The program generates the following files in the `results/` directory:

- `analysis_[chat_id].json` - Detailed analysis for each chat
- `analysis_summary.json` - Overall summary of all analyses
- `extracted_links.txt` - Links found in individual chat analysis
- `all_extracted_links.txt` - All unique links from all analyzed chats
- `extracted_links.json` - JSON format of extracted links

## Configuration

You can customize the analysis by modifying environment variables:

- `MESSAGE_LIMIT` - Maximum number of messages to analyze (0 = unlimited)
- `GET_MEMBERS` - Whether to extract member information
- `MEMBER_LIMIT` - Maximum number of members to analyze (0 = unlimited)

## Example output

```
🚀 Starting Telegram Chat Analyzer
============================================================
📋 Found 2 links to analyze
============================================================
🔍 Analysis 1/2: https://t.me/example_group
   📝 Retrieved 1500 messages
   👥 Retrieved 500 members
✅ Analysis completed: https://t.me/example_group
   📄 Results saved to: results/analysis_-1001234567890.json
🔍 Analysis 2/2: @example_channel
   📝 Retrieved 800 messages
   👥 Retrieved 300 members
✅ Analysis completed: @example_channel
   📄 Results saved to: results/analysis_-1009876543210.json
============================================================
📊 Final Summary:
   🔍 Total links checked: 2
   ✅ Successful analyses: 2
   📝 Total messages: 2,300
   👥 Total members: 800
   🔗 Total extracted links: 45
✅ Program completed successfully!
``` 