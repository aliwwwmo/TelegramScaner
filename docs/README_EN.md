# 🔍 Telegram Scanner - Advanced Telegram Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A powerful and comprehensive tool for analyzing, scanning, and processing Telegram groups and users information

## 📋 Table of Contents

- [🎯 Key Features](#-key-features)
- [🏗️ Project Structure](#️-project-structure)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [🔧 Configuration](#-configuration)
- [💻 Usage](#-usage)
- [📊 Advanced Features](#-advanced-features)
- [🐳 Docker](#-docker)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)

## 🎯 Key Features

### 🔍 **Main Scanner**
- ✅ **Group Scanning:** Complete analysis of Telegram groups and channels
- ✅ **User Extraction:** Comprehensive user information collection
- ✅ **Message Analysis:** Processing and analyzing group messages
- ✅ **Link Extraction:** Identifying and validating links
- ✅ **Reaction Tracking:** Analyzing reactions and forwards

### 🗄️ **Data Management**
- ✅ **MongoDB Storage:** Storing information in database
- ✅ **Saved Messages:** Sending results to Telegram
- ✅ **Auto Backup:** Secure data management
- ✅ **Reporting:** Comprehensive and analytical reports

### 🔄 **User JSON Processor**
- ✅ **Smart Merging:** Intelligent combination of user JSON files
- ✅ **History Combination:** Merging username_history and name_history
- ✅ **Duplicate Removal:** Preventing message and information duplication
- ✅ **Reprocessing:** Support for reprocessing with new files
- ✅ **Database Storage:** Storing final file information in database

### 🤖 **Smart Scanning**
- ✅ **Time Checking:** Preventing unnecessary scans
- ✅ **Continue from Last:** Continuing from last scanned message
- ✅ **Progress Display:** Showing remaining time
- ✅ **Group Management:** Reading groups from database

## 🏗️ Project Structure

```
TelegramScaner/
├── 📁 analyzer/                    # Main application folder
│   ├── 📁 config/                 # Configuration
│   ├── 📁 core/                   # Core application
│   ├── 📁 models/                 # Data models
│   ├── 📁 services/               # Main services
│   │   ├── telegram_client.py     # Telegram client
│   │   ├── telegram_storage.py    # Telegram storage
│   │   ├── mongo_service.py       # MongoDB service
│   │   ├── user_json_manager.py   # User JSON management
│   │   └── ...                    # Other services
│   ├── 📁 utils/                  # Utilities
│   ├── main.py                    # Main application
│   ├── user_json_processor.py     # User JSON processor
│   ├── quick_user_process.py      # Quick processing
│   └── README.md                  # Analyzer documentation
├── 📁 WebScraping/                # Web scraping section
│   ├── browser_manager.py         # Browser management
│   ├── data_collector.py          # Data collection
│   ├── telegram_scraper.py        # Telegram scraper
│   └── ...                        # Other files
├── 📁 testUserClientBot/          # User test bot
├── 📁 data/                       # Data
├── 📁 logs/                       # Logs
├── 🐳 docker-compose.yml          # Docker configuration
├── 🐳 Dockerfile                  # Docker file
├── 📄 env.example                 # Environment sample
└── 📄 README.md                   # This file
```

## 🚀 Quick Start

### With Docker (Recommended)
```bash
# 1. Clone the project
git clone <repository-url>
cd TelegramScaner

# 2. Set up environment file
cp env.example .env
# Edit .env file with your information

# 3. Start with Docker
docker-compose up -d

# 4. Run scanner
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python main.py"
```

### Without Docker
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment file
cp env.example .env
# Edit .env file

# 3. Run application
python analyzer/main.py
```

## 📦 Installation

### Prerequisites
- **Python 3.8+**
- **MongoDB** (or Docker)
- **Docker** (optional)
- **Telegram API** (API_ID and API_HASH)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Setup Telegram API
1. Go to [my.telegram.org](https://my.telegram.org)
2. Sign in and create a new application
3. Copy `API_ID` and `API_HASH`
4. Add them to `.env` file

## 🔧 Configuration

### `.env` File
```bash
# Telegram settings
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string

# MongoDB settings
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
MONGO_DATABASE=telegram_scanner
MONGO_COLLECTION=groups

# Storage settings
TELEGRAM_STORAGE_MODE=saved_messages

# Scan settings
MESSAGE_LIMIT=0
MEMBER_LIMIT=0
DEEP_SCAN=true
USE_DATABASE_FOR_GROUPS=true
SCAN_INTERVAL_MINUTES=30
```

### Advanced Settings
```bash
# Message settings
MESSAGE_BATCH_SIZE=200
DELAY_BETWEEN_BATCHES=0

# Member settings
MEMBER_BATCH_SIZE=500
GET_MEMBERS=true
INCLUDE_BOTS=true

# Analysis settings
EXTRACT_ALL_MESSAGES=true
EXTRACT_ALL_MEMBERS=true
EXTRACT_MEDIA_INFO=true
EXTRACT_REACTIONS=true
SAVE_MESSAGE_TEXT=true
ANALYZE_MEDIA=true
TRACK_REACTIONS=true
TRACK_FORWARDS=true
```

## 💻 Usage

### 1. Scan Groups
```bash
# Run main scanner
python analyzer/main.py

# Or with Docker
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python main.py"
```

### 2. Process User JSON Files
```bash
# Process a user
python analyzer/user_json_processor.py --user-id 123456789

# Quick processing
python analyzer/quick_user_process.py 123456789

# View processed users list
python analyzer/user_json_processor.py --list
```

### 3. Migrate Groups to Database
```bash
# Migrate groups from file to database
python analyzer/migrate_groups_to_db.py
```

### 4. Web Scraping
```bash
# Run web scraper
python WebScraping/main.py
```

## 📊 Advanced Features

### 🔍 **Smart Scanning**
- Check last scan time
- Continue from last scanned message
- Display remaining time
- Manage groups from database

### 📊 **Advanced Analysis**
- Analyze messages and content
- Extract and validate links
- Track reactions and forwards
- Analyze media and files

### 🗄️ **Data Management**
- Store in MongoDB
- Auto backup
- Comprehensive reporting
- Send to Saved Messages

### 🔄 **JSON Processor**
- Smart file merging
- Merge username and name history
- Remove duplicate messages
- Reprocess with new files

## 🐳 Docker

### Setup with Docker
```bash
# Build and run containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  telegram-scanner:
    build: .
    environment:
      - API_ID=${API_ID}
      - API_HASH=${API_HASH}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - mongodb
  
  mongodb:
    image: mongo:latest
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db
```

## 📚 Documentation

### 📖 Main Documentation
- [README_FINAL.md](README_FINAL.md) - Complete project documentation
- [analyzer/README.md](analyzer/README.md) - Analyzer documentation
- [DOCKER_README.md](DOCKER_README.md) - Docker guide

### 📋 Specific Features
- [DATABASE_GROUPS_FEATURE.md](DATABASE_GROUPS_FEATURE.md) - Database groups feature
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [MESSAGE_FILTERING.md](MESSAGE_FILTERING.md) - Message filtering
- [LINK_DETECTION_FEATURE.md](LINK_DETECTION_FEATURE.md) - Link detection
- [README_USER_JSON_PROCESSOR.md](README_USER_JSON_PROCESSOR.md) - JSON processor

### 🚀 Quick Guides
- [QUICK_START_DOCKER.md](QUICK_START_DOCKER.md) - Docker quick start
- [QUICK_START_FINAL.md](QUICK_START_FINAL.md) - Final quick start
- [QUICK_START_SMART_SCANNING.md](QUICK_START_SMART_SCANNING.md) - Smart scanning

## 🤝 Contributing

To contribute to the project:

1. **Fork** the repository
2. Create a new **branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### 🐛 Bug Reports
If you find a bug, please:
1. Report the issue in [Issues](https://github.com/your-repo/issues)
2. Provide complete details of the problem
3. Attach relevant logs

## 📄 License

This project is licensed under the **MIT** License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Telegram API** for providing powerful API
- **MongoDB** for excellent database
- **Python Community** for great tools
- **Docker** for containerization

---

**Developer:** AI Assistant  
**Last Updated:** 2025-01-27  
**Version:** 2.0  

⭐ If this project was helpful, please give it a star! 