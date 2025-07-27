@echo off
echo 🚀 Telegram Scanner Docker Setup
echo ================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed

REM Create necessary directories
echo 📁 Creating directories...
if not exist "results" mkdir results
if not exist "users" mkdir users
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    copy env.example .env >nul
    echo ✅ Created .env file. Please edit it with your Telegram API credentials.
    echo    Get your API credentials from: https://my.telegram.org/apps
) else (
    echo ✅ .env file already exists
)

REM Check if links.txt exists
if not exist "links.txt" (
    echo 📝 Creating sample links.txt file...
    (
        echo # Add your Telegram chat links here, one per line
        echo # Examples:
        echo # https://t.me/example_channel
        echo # @example_group
        echo # +1234567890  ^(for private chats^)
    ) > links.txt
    echo ✅ Created sample links.txt file. Please add your Telegram chat links.
) else (
    echo ✅ links.txt file already exists
)

REM Check if API credentials are set
findstr "your_api_id_here" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Warning: Please set your API credentials in .env file
    echo    Edit .env file and replace 'your_api_id_here' and 'your_api_hash_here'
    echo    with your actual Telegram API credentials
)

echo.
echo 🎯 Setup complete! Next steps:
echo 1. Edit .env file with your Telegram API credentials
echo 2. Edit links.txt file with your Telegram chat links
echo 3. Run: docker-compose up --build
echo.
echo 📚 For more information, see DOCKER_README.md
pause 