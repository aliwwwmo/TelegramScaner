# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome and ChromeDriver for Selenium
# RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable \
#     && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/logs /app/results /app/users /app/data

# Create a non-root user for security
RUN useradd -m -u 1000 telegramuser && \
    chown -R telegramuser:telegramuser /app

# Switch to non-root user
USER telegramuser

# Set default environment variables
ENV API_ID=""
ENV API_HASH=""
ENV SESSION_STRING=""
ENV MESSAGE_LIMIT="1000"
ENV MEMBER_LIMIT="5000"
ENV GET_MEMBERS="true"
ENV RESULTS_DIR="/app/results"
ENV USERS_DIR="/app/users"
ENV LOGS_DIR="/app/logs"
ENV LINKS_FILE="/app/links.txt"

# Expose port (if needed for web interface)
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"] 