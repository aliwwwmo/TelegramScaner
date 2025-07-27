.PHONY: help build up down logs clean setup test

# Default target
help:
	@echo "Telegram Scanner Docker Commands:"
	@echo ""
	@echo "  make setup    - Initial setup (create .env, directories)"
	@echo "  make build    - Build Docker image"
	@echo "  make up       - Start containers"
	@echo "  make down     - Stop containers"
	@echo "  make logs     - Show logs"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make test     - Test the setup"
	@echo "  make shell    - Open shell in container"
	@echo "  make restart  - Restart containers"

# Initial setup
setup:
	@echo "🚀 Setting up Telegram Scanner..."
	@mkdir -p results users logs data
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env file. Please edit it with your API credentials."; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@if [ ! -f links.txt ]; then \
		echo "# Add your Telegram chat links here, one per line" > links.txt; \
		echo "# Examples:" >> links.txt; \
		echo "# https://t.me/example_channel" >> links.txt; \
		echo "# @example_group" >> links.txt; \
		echo "✅ Created sample links.txt file"; \
	else \
		echo "✅ links.txt file already exists"; \
	fi
	@echo "🎯 Setup complete! Edit .env and links.txt files, then run 'make up'"

# Build Docker image
build:
	@echo "🔨 Building Docker image..."
	docker-compose build

# Start containers
up:
	@echo "🚀 Starting containers..."
	docker-compose up -d

# Start containers with build
up-build:
	@echo "🚀 Building and starting containers..."
	docker-compose up -d --build

# Stop containers
down:
	@echo "⏹️ Stopping containers..."
	docker-compose down

# Show logs
logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f

# Test setup
test:
	@echo "🧪 Testing setup..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if grep -q "your_api_id_here" .env; then \
		echo "⚠️  Warning: API credentials not set in .env file"; \
	fi
	@if [ ! -f links.txt ]; then \
		echo "❌ links.txt file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "✅ Setup looks good!"

# Open shell in container
shell:
	@echo "🐚 Opening shell in container..."
	docker-compose exec telegram-scanner bash

# Restart containers
restart:
	@echo "🔄 Restarting containers..."
	docker-compose restart

# Run with database
up-db:
	@echo "🗄️ Starting with database..."
	docker-compose --profile database up -d

# Show status
status:
	@echo "📊 Container status:"
	docker-compose ps

# Show resource usage
resources:
	@echo "💾 Resource usage:"
	docker stats --no-stream 