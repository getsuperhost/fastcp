# Use Python 3.9 slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV IS_DEBUG=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libmariadb-dev \
    pkg-config \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies and build assets
COPY package*.json ./
COPY webpack.mix.js ./
COPY resources/ ./resources/
RUN npm install
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN npm run production

# Copy project
COPY . .

# Create mock PHP directory for development
RUN mkdir -p /etc/php/8.1 /etc/php/8.0 /etc/php/7.4

# Create static files directory
RUN mkdir -p staticfiles

# Run Django commands
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "fastcp.wsgi:application"]