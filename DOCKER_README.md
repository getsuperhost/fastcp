# FastCP Docker Setup

FastCP is a Django-based web application for managing websites and databases. This document provides instructions for running FastCP using Docker.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- At least 2GB of available RAM
- At least 5GB of available disk space

## Quick Start

### Development Mode

1. **Clone the repository and navigate to the project directory:**

   ```bash
   cd /path/to/fastcp
   ```

2. **Build and start the application:**

   ```bash
   ./docker-run.sh build
   ./docker-run.sh up
   ```

3. **Access the application:**
   - Main application: `http://localhost:8899`
   - Admin panel: `http://localhost:8899/admin/`
   - API documentation: `http://localhost:8899/api/docs/`

### Production Mode

1. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

2. **Start in production mode:**

   ```bash
   ./docker-run.sh prod-up
   ```

## Development Workflow Improvements

### New Development Features

- **Hot Reloading**: Source code is mounted as volumes for instant code changes
- **Environment Configuration**: Support for `.env` files with development defaults
- **Makefile**: Convenient commands for common development tasks
- **Enhanced Testing**: pytest configuration with markers and coverage
- **Code Quality**: Automated linting, formatting, and security scanning
- **CI/CD Pipeline**: Updated CircleCI configuration with comprehensive testing

### Using the Makefile

The `Makefile` provides shortcuts for common development tasks:

```bash
# Install dependencies
make install

# Run development server
make dev-server

# Run tests
make test

# Format code
make format

# Run security scan
make security

# Clean up cache files
make clean
```

### Development with Docker

For the best development experience with Docker:

```bash
# Start with database (PostgreSQL)
docker-compose --profile with-db up -d

# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Open shell in container
docker-compose exec fastcp bash
```

### Testing and Quality Assurance

```bash
# Run all tests
make test

# Run linting
make lint

# Format code
make format

# Security scan
make security

# Check dependencies
make safety
```

## Docker Management Script

The `docker-run.sh` script provides convenient commands for managing the Docker environment:

### Available Commands

- `build` - Build the Docker image
- `up` - Start the application in development mode
- `down` - Stop the application
- `restart` - Restart the application
- `logs` - Show application logs
- `shell` - Open a shell in the running container
- `migrate` - Run Django database migrations
- `collectstatic` - Collect Django static files
- `createsuperuser` - Create a Django superuser
- `prod-up` - Start in production mode
- `prod-down` - Stop production mode
- `clean` - Remove containers and volumes (destructive)

### Usage Examples

```bash
# Build the application
./docker-run.sh build

# Start development environment
./docker-run.sh up

# View logs
./docker-run.sh logs -f

# Run database migrations
./docker-run.sh migrate

# Create admin user
./docker-run.sh createsuperuser

# Open shell in container
./docker-run.sh shell

# Stop and clean up
./docker-run.sh down
./docker-run.sh clean
```

## Manual Docker Commands

If you prefer to use Docker commands directly:

### Development

```bash
# Build the image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Production

```bash
# Start in production mode
docker-compose -f docker-compose.prod.yml up -d

# Stop production
docker-compose -f docker-compose.prod.yml down
```

## Environment Configuration

### Development (.env)

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=fastcp.settings
```

### Production Environment Setup

For production, set these additional environment variables:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@db:5432/fastcp
ALLOWED_HOSTS=your-domain.com
DJANGO_SETTINGS_MODULE=fastcp.settings
```

## Database

### SQLite (Development)

The application uses SQLite by default for development. The database file is stored in the container and persisted via Docker volumes.

### PostgreSQL (Production)

For production, configure PostgreSQL:

1. Update `DATABASE_URL` in your environment variables
2. The production Docker Compose includes a PostgreSQL service
3. Run migrations after starting the production environment

## File Structure

```text
fastcp/
├── Dockerfile                    # Main Docker image definition
├── docker-compose.yml           # Development environment
├── docker-compose.prod.yml      # Production environment
├── docker-run.sh               # Management script
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies
├── manage.py                  # Django management script
├── fastcp/                    # Django project directory
├── api/                       # Django apps
├── core/
├── staticfiles/               # Collected static files
└── db.sqlite3                 # SQLite database (development)
```

## Building Custom Images

### Development Image

```bash
docker build -t fastcp:dev .
```

### Production Image

```bash
docker build --target production -t fastcp:prod .
```

## Troubleshooting

### Common Issues

1. **Port 8899 already in use:**

   ```bash
   # Find process using port 8899
   lsof -i :8899
   # Kill the process or change the port in docker-compose.yml
   ```

2. **Permission denied on Linux:**

   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. **Database connection issues:**

   ```bash
   # Check database service logs
   ./docker-run.sh logs
   # Run migrations
   ./docker-run.sh migrate
   ```

4. **Static files not loading:**

   ```bash
   # Collect static files
   ./docker-run.sh collectstatic
   ```

### Logs and Debugging

```bash
# View all logs
./docker-run.sh logs

# View specific service logs
docker-compose logs fastcp

# Follow logs in real-time
./docker-run.sh logs -f

# Open shell for debugging
./docker-run.sh shell
```

### Container Health Checks

The application includes health checks that monitor:

- Django application responsiveness
- Database connectivity
- Static file serving

Check container health:

```bash
docker ps
# Look for "healthy" status in STATUS column
```

## Security Considerations

### Development Environment Security

- Debug mode is enabled
- All Django security features are disabled for development convenience
- Database is SQLite (not suitable for production)

### Production Environment Security

- Debug mode is disabled
- SECRET_KEY must be set to a secure random value
- ALLOWED_HOSTS must be configured
- Use HTTPS in production
- Regularly update base images and dependencies

## Performance Optimization

### Development Environment Performance

- Volume mounts for live code reloading
- SQLite database for fast development cycles
- Debug toolbar enabled

### Production Environment Performance

- Gunicorn WSGI server
- PostgreSQL database
- Static files served by Nginx
- Redis for caching (if configured)

## Backup and Restore

### Database Backup

```bash
# SQLite (development)
docker-compose exec fastcp sqlite3 /app/db.sqlite3 .dump > backup.sql

# PostgreSQL (production)
docker-compose -f docker-compose.prod.yml exec db pg_dump -U fastcp > backup.sql
```

### Database Restore

```bash
# SQLite
docker-compose exec fastcp sqlite3 /app/db.sqlite3 < backup.sql

# PostgreSQL
docker-compose -f docker-compose.prod.yml exec -T db psql -U fastcp < backup.sql
```

## Contributing

1. Make changes to the codebase
2. Test in development environment
3. Build and test production image
4. Submit pull request

## Support

For issues and questions:

1. Check the logs: `./docker-run.sh logs`
2. Verify Docker and Docker Compose versions
3. Ensure all prerequisites are met
4. Check the troubleshooting section above

## License

This project is licensed under the MIT License.
