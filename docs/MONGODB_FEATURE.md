# MongoDB Integration Feature

## Overview

This feature adds MongoDB database support to store basic information about Telegram groups and channels with minimal memory usage.

## Features

### Stored Information
- **ID**: Unique chat ID
- **Link**: Telegram link/username
- **Last Scan**: Timestamp of the last scan
- **Last Message**: ID of the last extracted message
- **Public/Private**: Whether the group is public or private
- **Scan Success**: Success/failure status of the last scan
- **Scan Count**: Number of times the group has been scanned

### Memory Optimization
- Minimal data storage (only essential information)
- Efficient indexing for fast queries
- Automatic cleanup of old records
- Optimized data structures

## Setup

### 1. Install MongoDB
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mongodb

# macOS
brew install mongodb-community

# Windows
# Download from https://www.mongodb.com/try/download/community
```

### 2. Install Python Dependencies
```bash
pip install pymongo>=4.5.0
```

### 3. Configure Environment Variables
Add these to your `.env` file:

```env
# MongoDB Settings
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups
```

## Usage

### Automatic Storage
When you run the analyzer, group information is automatically stored in MongoDB:

```bash
python main.py
```

### View Statistics
```bash
# View overall statistics
python mongo_stats.py stats

# View recent scans (last 24 hours)
python mongo_stats.py recent

# View recent scans (last 48 hours)
python mongo_stats.py recent 48

# View failed scans
python mongo_stats.py failed

# Search for a specific group
python mongo_stats.py search @group_username

# Clean up old records (older than 30 days)
python mongo_stats.py cleanup

# Clean up old records (older than 7 days)
python mongo_stats.py cleanup 7
```

## Database Schema

### GroupInfo Collection
```json
{
  "_id": "ObjectId",
  "chat_id": 123456789,
  "username": "group_username",
  "link": "https://t.me/group_username",
  "chat_type": "group|channel|supergroup|private",
  "is_public": true,
  "last_scan_time": "2024-01-01T12:00:00Z",
  "last_message_id": 12345,
  "last_scan_status": "success|failed|partial",
  "scan_count": 5,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Indexes

The following indexes are automatically created for optimal performance:

- `chat_id` (unique): Fast lookup by chat ID
- `username` (sparse): Fast lookup by username
- `last_scan_time`: For recent scan queries
- `last_scan_status`: For status-based queries

## API Reference

### MongoService Class

#### Methods

- `connect()`: Connect to MongoDB
- `disconnect()`: Disconnect from MongoDB
- `save_group_info(group_info)`: Save or update group information
- `get_group_info(chat_id)`: Get group by chat ID
- `get_group_by_username(username)`: Get group by username
- `get_groups_by_status(status)`: Get groups by scan status
- `get_recent_scans(hours)`: Get recently scanned groups
- `get_failed_scans()`: Get failed scans
- `get_successful_scans()`: Get successful scans
- `get_stats()`: Get overall statistics
- `delete_group(chat_id)`: Delete a group
- `cleanup_old_records(days)`: Clean up old records

### GroupInfo Class

#### Properties

- `chat_id`: Unique chat identifier
- `username`: Group username (optional)
- `link`: Group link
- `chat_type`: Type of chat (group/channel/supergroup/private)
- `is_public`: Whether group is public
- `last_scan_time`: Last scan timestamp
- `last_message_id`: ID of last extracted message
- `last_scan_status`: Success/failure status
- `scan_count`: Number of scans performed

#### Methods

- `to_dict()`: Convert to dictionary for MongoDB storage
- `from_dict(data)`: Create from MongoDB data
- `update_scan_info(message_id, status)`: Update scan information

## Error Handling

The MongoDB service includes comprehensive error handling:

- Connection failures are logged and handled gracefully
- Database operations are wrapped in try-catch blocks
- Failed operations don't stop the main analysis process
- Automatic reconnection attempts

## Performance Tips

1. **Use Indexes**: Indexes are automatically created for optimal performance
2. **Batch Operations**: For bulk operations, consider using batch inserts
3. **Cleanup**: Regularly run cleanup to remove old records
4. **Connection Pooling**: The service uses connection pooling for efficiency

## Troubleshooting

### Connection Issues
```bash
# Check if MongoDB is running
sudo systemctl status mongodb

# Start MongoDB if not running
sudo systemctl start mongodb
```

### Permission Issues
```bash
# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Database Size
```bash
# Check database size
mongo
use telegram_scanner
db.stats()
```

## Migration

If you have existing data, you can migrate it to the new MongoDB structure:

1. Export existing data
2. Transform to new schema
3. Import using the MongoService

## Future Enhancements

- Real-time statistics dashboard
- Advanced querying capabilities
- Data export/import tools
- Automated backup and restore
- Performance monitoring 