![fastcp-control-panel](https://fastcp.org/images/prototype.png "FastCP Control Panel")

# FastCP
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

## How to Install?
You can visit [https://fastcp.org](https://fastcp.org) to install FastCP on your server or you can execute the following command as root user on your Ubuntu server:

```bash
cd /home && sudo curl -o latest https://fastcp.org/latest.sh && sudo bash latest
```

## How to Update?
To update FastCP to latest version, execute this command as root user:
```bash
cd ~/ && sudo fastcp-updater
```

## Development Setup

### Prerequisites
* Python 3.12+
* Node.js 22+
* Docker and Docker Compose
* Git

### Local Development Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/getsuperhost/fastcp.git
   cd fastcp
   ```

2. **Set up Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies and build assets:**

   ```bash
   npm install
   npm run dev  # For development with hot reload
   # or
   npm run build  # For production build
   ```

5. **Set up the database:**

   ```bash
   docker-compose up -d db
   ```

6. **Run database migrations:**

   ```bash
   python manage.py migrate
   ```

7. **Create a superuser:**

   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server:**

   ```bash
   python manage.py runserver 8877
   ```

9. **Access the application:**
   * Open your browser and go to: <http://localhost:8877>
   * Login with the superuser credentials you created

### Development Commands

* **Run tests:** `python manage.py test`
* **Run linting:** `python manage.py check`
* **Collect static files:** `python manage.py collectstatic`
* **Build frontend assets:** `npm run build`
* **Watch frontend changes:** `npm run dev`

### Database Management

The development environment uses Docker Compose with MySQL 8.0. To manage the database:

```bash
# Start database
docker-compose up -d db

# Stop database
docker-compose down

# View database logs
docker-compose logs db

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up -d db
python manage.py migrate
```

### Environment Variables

Create a `.env` file in the project root for local configuration:

```env
DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql://fastcp:fastcppassword@localhost:3306/fastcp
IS_DEBUG=1
FASTCP_SQL_USER=fastcp
FASTCP_SQL_PASSWORD=fastcppassword
```

### Code Structure

* `api/` - REST API endpoints
* `core/` - Main application logic and models
* `fastcp/` - Django project settings
* `resources/` - Frontend source files
* `staticfiles/` - Compiled static assets
* `templates/` - HTML templates
* `manage.py` - Django management script
