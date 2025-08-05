# Quick Start with Docker (MongoDB Included)

This guide will help you set up and run the Telegram Scanner with MongoDB using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Telegram API credentials (API_ID and API_HASH)

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd TelegramScaner
```

### 2. Create Environment File
Copy the example environment file and configure it:
```bash
cp env.example .env
```

Edit `.env` file and add your Telegram API credentials:
```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

### 3. Create Links File
Create a `links.txt` file with your Telegram group/channel links:
```bash
# Example links.txt
https://t.me/example_channel
@example_group
+1234567890
```

### 4. Run with Docker Compose
```bash
# Start all services (Telegram Scanner + MongoDB)
docker-compose up -d

# View logs
docker-compose logs -f telegram-scanner

# Stop services
docker-compose down
```

## Services

### Telegram Scanner
- **Container**: `telegram-scanner`
- **Port**: 8000 (for potential web interface)
- **Dependencies**: MongoDB

### MongoDB
- **Container**: `telegram-scanner-mongo`
- **Port**: 27017
- **Credentials**: admin/password
- **Database**: telegram_scanner

## Data Persistence

The following data is persisted:
- **MongoDB Data**: `mongodb_data` volume
- **Results**: `./results` directory
- **Users**: `./users` directory
- **Logs**: `./logs` directory

## MongoDB Management

### View Statistics
```bash
# Access MongoDB container
docker exec -it telegram-scanner-mongo mongosh

# Switch to database
use telegram_scanner

# View collections
show collections

# View groups
db.groups.find()

# View statistics
db.groups.aggregate([
  {
    $group: {
      _id: null,
      total: { $sum: 1 },
      successful: { $sum: { $cond: [{ $eq: ["$last_scan_status", "success"] }, 1, 0] } },
      failed: { $sum: { $cond: [{ $eq: ["$last_scan_status", "failed"] }, 1, 0] } }
    }
  }
])
```

### Backup MongoDB Data
```bash
# Create backup
docker exec telegram-scanner-mongo mongodump --db telegram_scanner --out /data/backup

# Copy backup from container
docker cp telegram-scanner-mongo:/data/backup ./mongodb_backup
```

### Restore MongoDB Data
```bash
# Copy backup to container
docker cp ./mongodb_backup telegram-scanner-mongo:/data/backup

# Restore data
docker exec telegram-scanner-mongo mongorestore --db telegram_scanner /data/backup/telegram_scanner
```

## Troubleshooting

### Check Service Status
```bash
# Check all services
docker-compose ps

# Check MongoDB logs
docker-compose logs mongodb

# Check Telegram Scanner logs
docker-compose logs telegram-scanner
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove all data
sudo rm -rf ./results ./users ./logs

# Start fresh
docker-compose up -d
```

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
docker exec telegram-scanner-mongo mongosh --eval "db.adminCommand('ping')"

# Restart MongoDB
docker-compose restart mongodb
```

## Environment Variables

Key environment variables for Docker:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_ID` | - | Telegram API ID (required) |
| `API_HASH` | - | Telegram API Hash (required) |
| `MONGO_CONNECTION_STRING` | `mongodb://admin:password@mongodb:27017/` | MongoDB connection |
| `MONGO_DATABASE` | `telegram_scanner` | Database name |
| `MONGO_COLLECTION` | `groups` | Collection name |

## Performance

The Docker setup includes:
- **Resource Limits**: 2GB RAM, 1 CPU
- **Health Checks**: Automatic service monitoring
- **Auto-restart**: Services restart automatically
- **Volume Persistence**: Data survives container restarts

## Security

- MongoDB runs with authentication (admin/password)
- Non-root user for the application
- Isolated network between services
- Volume mounts for data persistence 