# 🔍 Telegram Scanner - Advanced Telegram Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A powerful and comprehensive tool for analyzing, scanning, and processing Telegram groups and users information

## 🌍 Language Versions

- 🇺🇸 **[English Version](docs/README_EN.md)** - Complete English documentation
- 🇮🇷 **[Persian Version](docs/README_FA.md)** - مستندات کامل فارسی

## 📋 Quick Overview

### 🎯 **Key Features**
- ✅ **Group Scanning:** Complete analysis of Telegram groups and channels
- ✅ **User Extraction:** Comprehensive user information collection
- ✅ **Message Analysis:** Processing and analyzing group messages
- ✅ **Link Extraction:** Identifying and validating links
- ✅ **Smart JSON Processing:** Intelligent user data merging
- ✅ **MongoDB Storage:** Secure data management
- ✅ **Docker Support:** Easy deployment

### 🚀 **Quick Start**
```bash
# Clone and setup
git clone <repository-url>
cd TelegramScaner
cp env.example .env

# With Docker (Recommended)
docker-compose up -d
docker exec -it telegram-scanner /bin/bash -c "cd /app/analyzer && python main.py"

# Without Docker
pip install -r requirements.txt
python analyzer/main.py
```

### 📊 **Project Structure**
```
TelegramScaner/
├── 📁 analyzer/          # Main application
├── 📁 WebScraping/       # Web scraping tools
├── 📁 testUserClientBot/ # Test bot
├── 📁 docs/              # Documentation
├── 🐳 docker-compose.yml # Docker configuration
└── 📄 README.md          # This file
```

## 📚 Documentation

### 📖 **Main Documentation**
- **[English](docs/README_EN.md)** - Complete English guide
- **[Persian](docs/README_FA.md)** - راهنمای کامل فارسی
- **[Final Docs](docs/README_FINAL.md)** - Comprehensive project documentation

### 🔧 **Technical Guides**
- **[Analyzer Docs](analyzer/README.md)** - Main analyzer documentation
- **[Docker Guide EN](docs/DOCKER_README_EN.md)** - English Docker setup
- **[Docker Guide FA](docs/DOCKER_README_FA.md)** - راهنمای Docker فارسی
- **[Docker Guide](docs/DOCKER_README.md)** - Docker setup and usage
- **[Quick Start EN](docs/QUICK_START_EN.md)** - English quick start
- **[Quick Start FA](docs/QUICK_START_FA.md)** - راهنمای سریع فارسی
- **[Quick Start](docs/QUICK_START_DOCKER.md)** - Quick setup guide

### 📋 **Feature Documentation**
- **[Database Groups](docs/DATABASE_GROUPS_FEATURE.md)** - Database groups feature
- **[Message Filtering](docs/MESSAGE_FILTERING.md)** - Message filtering capabilities
- **[Link Detection](docs/LINK_DETECTION_FEATURE.md)** - Link detection feature
- **[JSON Processor](docs/README_USER_JSON_PROCESSOR.md)** - User JSON processing
- **[Smart Scanning](docs/SMART_SCANNING_FEATURE.md)** - Smart scanning feature
- **[MongoDB Feature](docs/MONGODB_FEATURE.md)** - MongoDB integration
- **[User Storage](docs/USER_STORAGE_FEATURE.md)** - User storage feature

### 🚀 **Quick Guides**
- **[Docker Quick Start](docs/QUICK_START_DOCKER.md)** - Docker quick start
- **[Final Quick Start](docs/QUICK_START_FINAL.md)** - Final quick start
- **[Smart Scanning](docs/QUICK_START_SMART_SCANNING.md)** - Smart scanning guide
- **[General Quick Start](docs/QUICK_START.md)** - General quick start

### 🆕 **New Features**
- **[New Features](docs/README_NEW_FEATURES.md)** - Latest features overview
- **[Group Filtering](docs/GROUP_FILTERING.md)** - Group filtering capabilities

## 🛠️ **Prerequisites**
- **Python 3.8+**
- **MongoDB** (or Docker)
- **Telegram API** (API_ID and API_HASH)

## 🔧 **Configuration**
```bash
# Required environment variables
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
MONGO_CONNECTION_STRING=mongodb://admin:password@mongodb:27017/
```

## 💻 **Usage Examples**

### Scan Groups
```bash
python analyzer/main.py
```

### Process User JSON
```bash
python analyzer/user_json_processor.py --user-id 123456789
```

### Web Scraping
```bash
python WebScraping/main.py
```

## 🤝 **Contributing**

1. **Fork** the repository
2. Create a **branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

## 📄 **License**

This project is licensed under the **MIT** License. See the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Telegram API** for providing powerful API
- **MongoDB** for excellent database
- **Python Community** for great tools
- **Docker** for containerization

---

**Developer:** AI Assistant  
**Last Updated:** 2025-01-27  
**Version:** 2.0  

⭐ If this project was helpful, please give it a star!

---

> **Note:** For detailed documentation, please refer to the language-specific README files:
> - 🇺🇸 [English Documentation](docs/README_EN.md)
> - 🇮🇷 [مستندات فارسی](docs/README_FA.md) 