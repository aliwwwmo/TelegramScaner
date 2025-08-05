# Message Filtering Configuration

## Overview
This document explains how to configure message filtering to exclude specific messages (like `scan_start_message`) from being stored in MongoDB.

## Filter Settings

The system now includes configurable message filtering that can be controlled through environment variables:

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FILTER_SCAN_MESSAGES` | `true` | Enable/disable filtering of scan-related messages |
| `FILTER_BOT_MESSAGES` | `true` | Enable/disable filtering of bot messages |
| `FILTER_SYSTEM_MESSAGES` | `true` | Enable/disable filtering of system messages |

### Scan Keywords
The following keywords are used to identify scan-related messages:
- `scan_start_message`
- `scan start`
- `اسکن شروع`
- `شروع اسکن`
- `scanning started`
- `scan initiated`

### Bot Keywords
The following keywords are used to identify bot/system messages:
- `bot`
- `system`
- `automated`
- `scan`
- `analysis`

## Configuration Examples

### Enable All Filtering (Default)
```bash
FILTER_SCAN_MESSAGES=true
FILTER_BOT_MESSAGES=true
FILTER_SYSTEM_MESSAGES=true
```

### Disable Scan Message Filtering
```bash
FILTER_SCAN_MESSAGES=false
```

### Disable All Filtering
```bash
FILTER_SCAN_MESSAGES=false
FILTER_BOT_MESSAGES=false
FILTER_SYSTEM_MESSAGES=false
```

## How It Works

1. **Message Collection**: Messages are filtered during collection in `telegram_client.py`
2. **Message Processing**: Messages are filtered during processing in `message_analyzer.py`
3. **Main Analysis**: Messages are filtered in the main analysis loop in `main.py`

## Logging

When a message is filtered, you'll see log messages like:
```
⏭️ Skipping scan start message: 12345
⏭️ Skipping bot/system message: 12346
```

## Customization

To add custom keywords, you can modify the `FilterSettings` class in `config/settings.py`:

```python
scan_keywords=[
    'scan_start_message',
    'scan start',
    'اسکن شروع',
    'شروع اسکن',
    'scanning started',
    'scan initiated',
    'your_custom_keyword'  # Add your custom keywords here
]
```

## Benefits

- **Prevents Data Pollution**: Scan messages won't be stored in MongoDB
- **Configurable**: Easy to enable/disable filtering
- **Extensible**: Easy to add new keywords
- **Logging**: Clear visibility of what's being filtered
- **Performance**: Filtering happens at multiple levels for efficiency 