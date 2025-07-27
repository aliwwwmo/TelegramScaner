#!/bin/bash

echo "🚀 Telegram Scanner Docker Setup"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p results users logs data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ Created .env file. Please edit it with your Telegram API credentials."
    echo "   Get your API credentials from: https://my.telegram.org/apps"
else
    echo "✅ .env file already exists"
fi

# Check if links.txt exists
if [ ! -f links.txt ]; then
    echo "📝 Creating sample links.txt file..."
    cat > links.txt << EOF
# Add your Telegram chat links here, one per line
# Examples:
# https://t.me/example_channel
# @example_group
# +1234567890  (for private chats)
EOF
    echo "✅ Created sample links.txt file. Please add your Telegram chat links."
else
    echo "✅ links.txt file already exists"
fi

# Check if API credentials are set
if grep -q "your_api_id_here" .env; then
    echo "⚠️  Warning: Please set your API credentials in .env file"
    echo "   Edit .env file and replace 'your_api_id_here' and 'your_api_hash_here'"
    echo "   with your actual Telegram API credentials"
fi

echo ""
echo "🎯 Setup complete! Next steps:"
echo "1. Edit .env file with your Telegram API credentials"
echo "2. Edit links.txt file with your Telegram chat links"
echo "3. Run: docker-compose up --build"
echo ""
echo "📚 For more information, see DOCKER_README.md" 