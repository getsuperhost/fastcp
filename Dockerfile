# Use Python 3.12 slim image
FROM python:3.12-slim

# Add metadata labels
LABEL maintainer="FastCP Team"
LABEL version="1.1.0"
LABEL description="FastCP - Fast Control Panel"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=fastcp.settings
ENV IS_DEBUG=1

# Install system dependencies with security updates
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy package files for Node.js dependencies
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build frontend assets
RUN npm run production

# Create necessary directories
RUN mkdir -p staticfiles logs tmp

# Run Django migrations and collect static files
RUN python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8899

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8899"]
