#!/bin/bash
set -e

echo "🚀 Starting Telegram Scanner..."

# Check if required environment variables are set
if [ -z "$API_ID" ] || [ -z "$API_HASH" ]; then
    echo "❌ Error: API_ID and API_HASH environment variables are required!"
    echo "Please set them in your .env file or environment."
    echo "You can get these from https://my.telegram.org/apps"
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p /app/results /app/users /app/logs /app/data

# Check if links.txt exists, create sample if not
if [ ! -f /app/links.txt ]; then
    echo "📝 Creating sample links.txt file..."
    cat > /app/links.txt << EOF
# Add your Telegram chat links here, one per line
# Examples:
# https://t.me/example_channel
# @example_group
# +1234567890  (for private chats)
EOF
    echo "✅ Created sample links.txt file"
fi

# Check if .env file exists
if [ ! -f /app/.env ]; then
    echo "⚠️  Warning: .env file not found. Using environment variables."
fi

# Display configuration
echo "📋 Configuration:"
echo "   API ID: ${API_ID}"
echo "   Message Limit: ${MESSAGE_LIMIT:-1000}"
echo "   Member Limit: ${MEMBER_LIMIT:-5000}"
echo "   Get Members: ${GET_MEMBERS:-true}"
echo "   Results Dir: ${RESULTS_DIR:-/app/results}"

# Run the main application
echo "🔍 Starting analysis..."
exec python /app/analyzer/main.py 