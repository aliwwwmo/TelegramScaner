# Telegram Analyzer - Complete Feature Set

## 🚀 Main Features

### 1. **Message Analysis**
- Extract messages from Telegram groups and channels
- Analyze message content and metadata
- Track message reactions and forwards
- Process both text messages and media captions

### 2. **Member Tracking**
- Extract detailed member information
- Track user activity and engagement
- Monitor username and name changes
- Identify bots and deleted accounts

### 3. **Link Detection & Extraction** ⭐ NEW
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

### 4. **URL Resolution**
- Resolve redirect links to find actual Telegram links
- Handle Google Translate and other redirect services
- Validate and categorize link types
- Track redirect chains

### 5. **Comprehensive Reporting**
- Generate detailed JSON reports
- Create user activity summaries
- Export data in multiple formats
- Provide statistical analysis

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
│   └── file_manager.py              # File operations
├── models/
│   └── data_models.py               # Data structures
├── utils/
│   └── logger.py                    # Logging
└── results/                         # Output directory
    ├── extracted_links.txt          # Individual chat links
    ├── all_extracted_links.txt      # Combined links
    └── sample_extracted_links.txt   # Sample format
```

## 🔧 Configuration

### Environment Variables (.env)
```env
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
MESSAGES_PER_CHAT=1000
RESULTS_DIR=results
USERS_DIR=users
LINKS_FILE=links.txt
OUTPUT_FILE=my_chats.json
```

### Input File (links.txt)
```
https://t.me/example_channel
@example_group
+1234567890
https://t.me/joinchat/HASH
```

## 📊 Output Files

### Analysis Results
- `my_chats.json` - Main analysis summary
- `analysis_summary.json` - Detailed summary
- `users/user_[id].json` - Individual user data

### Link Detection Results
- `extracted_links.txt` - Links from current chat
- `all_extracted_links.txt` - All unique links
- `extracted_links.json` - JSON format

## 🎯 Usage

### 1. Setup
```bash
cd analyzer
# Edit .env with your API credentials
# Add chat links to links.txt
```

### 2. Run Analysis
```bash
python main.py
```

### 3. Check Results
```bash
# View extracted links
cat results/extracted_links.txt
cat results/all_extracted_links.txt

# View analysis summary
cat my_chats.json
```

## 📈 Features in Detail

### Link Detection System
- **Real-time extraction**: Links are extracted as messages are processed
- **Multiple formats**: Supports all common Telegram link formats
- **Duplicate prevention**: Uses sets to avoid duplicate links
- **File organization**: Saves links in both individual and combined files
- **Comprehensive logging**: Tracks extraction statistics

### Message Processing
- **Text analysis**: Processes both message text and captions
- **Link extraction**: Automatically finds and extracts links
- **User tracking**: Monitors user activity and changes
- **Metadata capture**: Records reactions, forwards, edits

### Data Management
- **Structured storage**: JSON format for easy processing
- **User profiles**: Detailed user activity tracking
- **Link categorization**: Classifies different link types
- **Statistical reporting**: Provides comprehensive analytics

## 🔍 Monitoring

The system provides detailed logging:
```
🚀 Starting Telegram Chat Analyzer...
📋 Found 2 chat(s) to analyze
🔍 Analyzing chat 1/2: https://t.me/example
   📝 Processing 1500 messages...
   🔗 Extracted links saved to: results/extracted_links.txt
   📊 Total extracted links: 45
✅ Chat 1 completed successfully
🔗 All extracted links saved to: results/all_extracted_links.txt
   📊 Total unique links found: 78
✅ Analysis completed! Processed 2 chats
```

## 🛠️ Technical Details

### Link Detection Patterns
```python
patterns = [
    r'https?://[^\s<>"\']+',    # Full URLs
    r'www\.[^\s<>"\']+',        # www URLs
    r't\.me/[^\s<>"\']+',       # Short Telegram links
    r'@[a-zA-Z0-9_]+',          # Username mentions
]
```

### Supported Link Types
- **Public channels**: `https://t.me/channel`
- **Private groups**: `https://t.me/joinchat/HASH`
- **Username mentions**: `@username`
- **Short links**: `t.me/username`
- **Regular URLs**: `https://example.com`

## ✅ Quality Assurance

- **Error handling**: Graceful handling of API errors
- **Rate limiting**: Respects Telegram API limits
- **Data validation**: Validates all extracted data
- **File integrity**: Ensures proper file saving
- **Logging**: Comprehensive activity tracking

## 🚀 Ready for Production

The system is now fully functional and ready for production use. All features are integrated and tested, with comprehensive documentation and error handling. 