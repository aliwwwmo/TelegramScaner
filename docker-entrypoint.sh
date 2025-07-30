#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Telegram Scanner with MongoDB..."

# Check if required environment variables are set
if [ -z "$API_ID" ] || [ -z "$API_HASH" ]; then
    echo "❌ Error: API_ID and API_HASH must be set"
    echo "Please set these in your .env file or environment variables"
    exit 1
fi

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
until python -c "
import pymongo
import time
import os

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        client = pymongo.MongoClient('mongodb://admin:password@mongodb:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print('✅ MongoDB is ready!')
        client.close()
        exit(0)
    except Exception as e:
        attempt += 1
        print(f'⏳ Attempt {attempt}/{max_attempts}: MongoDB not ready yet...')
        time.sleep(2)

print('❌ MongoDB connection failed after 30 attempts')
exit(1)
"; do
    echo "⏳ MongoDB is not ready yet, waiting..."
    sleep 2
done

# Create necessary directories if they don't exist
mkdir -p /app/logs /app/results /app/users /app/data

# Check if links.txt exists, create if not
if [ ! -f /app/links.txt ]; then
    echo "📝 Creating sample links.txt file..."
    cat > /app/links.txt << EOF
# Add your Telegram chat links here, one per line
# Examples:
# https://t.me/example_channel
# @example_group
# +1234567890  (for private chats)
EOF
fi

# Run the main application
echo "🎯 Starting Telegram Scanner..."
cd /app/analyzer
#python main.py 
tail -f /dev/null
