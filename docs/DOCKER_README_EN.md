# Telegram Scanner - Docker Setup

This Telegram Scanner project is now runnable with Docker!

## 🚀 Quick Start

### 1. Install Docker and Docker Compose

First install Docker and Docker Compose:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Or [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Configure API Credentials

Create the `.env` file:

```bash
cp env.example .env
```

Then edit the `.env` file and enter your Telegram API credentials:

```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

**Note:** Get API credentials from [https://my.telegram.org/apps](https://my.telegram.org/apps).

### 3. Configure Telegram Links

Edit the `links.txt` file and add Telegram links:

```txt
https://t.me/example_channel
@example_group
+1234567890
```

### 4. Run Docker Container

```bash
# Build and run container
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

## 📁 File Structure

```
TelegramScaner/
├── analyzer/           # Main analyzer code
├── WebScraping/       # Web scraping component
├── testUserClientBot/ # Test client
├── results/           # Analysis results (mounted volume)
├── users/             # User information (mounted volume)
├── logs/              # Log files (mounted volume)
├── data/              # Additional data (mounted volume)
├── links.txt          # Telegram links
├── .env               # Environment settings
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── requirements.txt   # Python dependencies
```

## ⚙️ Advanced Settings

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_ID` | - | Telegram API ID (required) |
| `API_HASH` | - | Telegram API Hash (required) |
| `SESSION_STRING` | - | Session string for quick login |
| `MESSAGE_LIMIT` | 1000 | Maximum number of messages |
| `MEMBER_LIMIT` | 5000 | Maximum number of members |
| `GET_MEMBERS` | true | Get member information |
| `INCLUDE_BOTS` | true | Include bots |

### File Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `RESULTS_DIR` | /app/results | Results folder |
| `USERS_DIR` | /app/users | User information folder |
| `LOGS_DIR` | /app/logs | Logs folder |
| `LINKS_FILE` | /app/links.txt | Links file |

## 🔧 Useful Commands

### Run Analysis
```bash
# Full run
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Container Management
```bash
# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild
docker-compose up --build

# Run shell in container
docker-compose exec telegram-scanner bash
```

### Manual Execution
```bash
# Run analyzer
docker run --rm -v $(pwd)/results:/app/results -v $(pwd)/links.txt:/app/links.txt -e API_ID=your_id -e API_HASH=your_hash telegram-scanner

# Run web scraper
docker run --rm -v $(pwd)/data:/app/data telegram-scanner python WebScraping/main.py
```

## 📊 Results

Analysis results are saved in the `results/` folder:

- `my_chats.json` - Complete analysis results
- `extracted_links.txt` - Extracted links
- `all_extracted_links.txt` - All unique links

## 🔍 Troubleshooting

### Common Errors

1. **Invalid API credentials**
   ```
   ❌ Error: API_ID and API_HASH environment variables are required!
   ```
   - Check API credentials in `.env` file
   - Get them from [https://my.telegram.org/apps](https://my.telegram.org/apps)

2. **Chrome/Selenium error**
   ```
   ChromeDriver error
   ```
   - Docker image includes Chrome
   - If problem persists, rebuild the container

3. **Rate Limit error**
   ```
   FloodWait error
   ```
   - Telegram has applied rate limit
   - Wait and try again

### Logs

```bash
# View container logs
docker-compose logs telegram-scanner

# View real-time logs
docker-compose logs -f telegram-scanner

# View file logs
tail -f logs/telegram_analysis.log
```

## 🗄️ Database (Optional)

To use MongoDB:

```bash
# Run with database
docker-compose --profile database up

# Or just database
docker-compose --profile database up mongodb
```

## 🔒 Security

- Container runs with non-root user
- Sensitive files are stored in separate volumes
- API credentials are protected in environment variables

## 📈 Performance

### Recommended Settings

```env
# For quick analysis
MESSAGE_LIMIT=500
MEMBER_LIMIT=1000
DELAY_BETWEEN_BATCHES=2

# For complete analysis
MESSAGE_LIMIT=5000
MEMBER_LIMIT=10000
DELAY_BETWEEN_BATCHES=1
```

### Resource Limits

Container runs with resource limits:
- Memory: 2GB max, 512MB reserved
- CPU: 1 core max, 0.5 core reserved

## 🤝 Contributing

To improve Docker setup:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## 📞 Support

If you have issues:
1. Check the logs
2. Read this README
3. Create an issue on GitHub 