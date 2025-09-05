# FastCP

<!-- ![fastcp-control-panel](https://fastcp.org/images/prototype.png "FastCP Control Panel") -->

FastCP is an open source control panel for Ubuntu servers. You can use FastCP to deploy and manage multiple PHP / WordPress websites on a single server. ServerPilot's simplicity and powerful features are the inspiration behind FastCP's development. Moreover, I have developed this control panel as the final project of my CS50 online course.

## Features

* Host multiple websites on a single server
* Create multiple SSH users
* Sub users can manage their websites
* Limit on websites and databases for sub users
* Auto WordPress deploy
* Fully isolated user data using ACLs
* NGINX reverse proxy on Apache for performance + htaccess support
* Multiple PHP versions support. Change PHP version per website with a single click
* Auto SSLs from Let's Encrypt with auto renewal

## Requirements

FastCP only supports the latest LTS versions of Ubuntu starting 20.04. Please beware although it will run on non-LTS releases too, but we have imposed a strict requirement of LTS releases only. At the moment, FastCP supports the following Ubuntu releases:

* Ubuntu 20.04 LTS

## Quick Start with Docker

### Prerequisites

* Docker and Docker Compose installed
* At least 2GB RAM available

### Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/getsuperhost/fastcp.git
   cd fastcp
   ```

2. **Start the development environment**

   ```bash
   docker compose up -d --build
   ```

3. **Access the application**
   * Web interface: [http://localhost:8899](http://localhost:8899)
   * Django admin: [http://localhost:8899/admin/](http://localhost:8899/admin/)

4. **Run management commands**

   ```bash
   docker compose exec fastcp python manage.py <command>
   ```

5. **Stop the environment**

   ```bash
   docker compose down
   ```

## Development

### Code Quality Tools

This project uses several tools to maintain code quality:

* **Black**: Code formatting
* **isort**: Import sorting
* **flake8**: Linting
* **bandit**: Security scanning
* **safety**: Dependency vulnerability scanning

### Running Tests

```bash
# Run all tests
docker compose exec fastcp python manage.py test

# Run specific app tests
docker compose exec fastcp python manage.py test core

# Run with coverage
docker compose exec fastcp python manage.py test --verbosity=2
```

### Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Security scan
bandit -r .

# Dependency security check
safety check
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
pip install pre-commit
pre-commit install
```

## Production Installation

You can visit [https://fastcp.org](https://fastcp.org) to install FastCP on your server or you can execute the following command as root user on your Ubuntu server:

```bash
cd /home && sudo curl -o latest https://fastcp.org/latest.sh && sudo bash latest
```

## Production Update

To update FastCP to latest version, execute this command as root user:

```bash
cd ~/ && sudo fastcp-updater
```

## API Documentation

FastCP provides a REST API for managing websites, users, databases, and more. The API is available at `/api/` and includes:

* **Websites**: CRUD operations, PHP version management, SSL certificates
* **Users**: SSH user management with resource limits
* **Databases**: MySQL database management
* **File Manager**: File system operations
* **Stats**: Usage statistics and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For support and questions:

* GitHub Issues: [https://github.com/getsuperhost/fastcp/issues](https://github.com/getsuperhost/fastcp/issues)
* Documentation: [https://fastcp.org/docs](https://fastcp.org/docs)
* Community Forum: [https://fastcp.org/forum](https://fastcp.org/forum)
