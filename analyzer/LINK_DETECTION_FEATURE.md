# Link Detection Feature

## Overview
This feature automatically detects and extracts links from Telegram messages during analysis. When links are found in messages, they are saved to files for further processing.

## How it works

### 1. Link Extraction
- The `MessageAnalyzer` class processes each message and extracts links using the `LinkAnalyzer`
- Links are extracted from both message text and captions
- Multiple link formats are supported:
  - `https://t.me/channel_name`
  - `@username`
  - `t.me/username`
  - `https://t.me/joinchat/HASH` (invite links)
  - Regular URLs that might contain Telegram links

### 2. Link Storage
- Extracted links are stored in a set to avoid duplicates
- Links are saved to files in the `results` directory:
  - `extracted_links.txt` - Individual chat links
  - `all_extracted_links.txt` - Combined links from all chats
  - `extracted_links.json` - JSON format for programmatic access

### 3. File Structure
```
analyzer/
├── results/
│   ├── extracted_links.txt          # Links from current analysis
│   ├── all_extracted_links.txt      # All unique links found
│   └── extracted_links.json         # JSON format
├── services/
│   ├── message_analyzer.py          # Main message processing
│   └── link_analyzer.py             # Link extraction logic
└── main.py                          # Main application
```

## Usage

### Running the Analyzer
```bash
cd analyzer
python main.py
```

### Configuration
The feature uses the following configuration from `.env`:
- `RESULTS_DIR=results` - Directory to save extracted links
- `MESSAGES_PER_CHAT=1000` - Number of messages to analyze per chat
- `LINKS_FILE=links.txt` - File containing chat links to analyze

### Output Files
1. **extracted_links.txt** - Links found in the current chat analysis
2. **all_extracted_links.txt** - All unique links from all analyzed chats
3. **extracted_links.json** - JSON format of extracted links

## Link Detection Patterns

The system detects the following link patterns:
- Full URLs: `https://t.me/channel`
- Username mentions: `@username`
- Short format: `t.me/username`
- Invite links: `https://t.me/joinchat/HASH`
- Regular URLs: `https://example.com`

## Testing

The link extraction functionality is automatically tested during the main analysis process. The system logs all extracted links and provides statistics on the number of links found per chat.

## Integration

The link detection is automatically integrated into the main analysis flow:
1. Messages are processed by `MessageAnalyzer`
2. Links are extracted using `LinkAnalyzer.extract_links_from_text()`
3. Links are stored in `message_analyzer.extracted_links`
4. Links are saved to files at the end of analysis

## Logging

The system logs link extraction activities:
- Number of links extracted per chat
- Total unique links found
- File save locations
- Link extraction statistics 