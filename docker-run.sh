#!/bin/bash
#
# FastCP Docker Management Script

set -e

COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
usage() {
    echo "FastCP Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build          Build the Docker image"
    echo "  up             Start the application"
    echo "  down           Stop the application"
    echo "  restart        Restart the application"
    echo "  logs           Show application logs"
    echo "  shell          Open a shell in the container"
    echo "  migrate        Run Django migrations"
    echo "  collectstatic  Collect Django static files"
    echo "  createsuperuser Create Django superuser"
    echo "  prod-up        Start in production mode"
    echo "  prod-down      Stop production mode"
    echo "  clean          Remove containers and volumes"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 up"
    echo "  $0 logs -f"
    echo "  $0 prod-up"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_compose() {
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        print_error "docker-compose is not installed."
        exit 1
    fi
}

# Function to use docker compose (newer syntax) or docker-compose (older)
compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

# Main script logic
main() {
    local cmd=$1
    shift

    case $cmd in
        build)
            check_docker
            print_info "Building Docker image..."
            $(compose_cmd) -f $COMPOSE_FILE build "$@"
            print_success "Docker image built successfully!"
            ;;
        up)
            check_docker
            print_info "Starting FastCP application..."
            $(compose_cmd) -f $COMPOSE_FILE up -d "$@"
            print_success "FastCP is running at http://localhost:8899"
            print_info "Admin panel: http://localhost:8899/admin/"
            ;;
        down)
            check_docker
            print_info "Stopping FastCP application..."
            $(compose_cmd) -f $COMPOSE_FILE down "$@"
            print_success "FastCP stopped successfully!"
            ;;
        restart)
            check_docker
            print_info "Restarting FastCP application..."
            $(compose_cmd) -f $COMPOSE_FILE restart "$@"
            print_success "FastCP restarted successfully!"
            ;;
        logs)
            check_docker
            $(compose_cmd) -f $COMPOSE_FILE logs "$@"
            ;;
        shell)
            check_docker
            print_info "Opening shell in FastCP container..."
            $(compose_cmd) -f $COMPOSE_FILE exec fastcp bash
            ;;
        migrate)
            check_docker
            print_info "Running Django migrations..."
            $(compose_cmd) -f $COMPOSE_FILE exec fastcp python manage.py migrate
            print_success "Migrations completed!"
            ;;
        collectstatic)
            check_docker
            print_info "Collecting Django static files..."
            $(compose_cmd) -f $COMPOSE_FILE exec fastcp python manage.py collectstatic --noinput
            print_success "Static files collected!"
            ;;
        createsuperuser)
            check_docker
            print_info "Creating Django superuser..."
            $(compose_cmd) -f $COMPOSE_FILE exec fastcp python manage.py createsuperuser
            ;;
        prod-up)
            check_docker
            print_info "Starting FastCP in production mode..."
            $(compose_cmd) -f $PROD_COMPOSE_FILE up -d "$@"
            print_success "FastCP production mode is running at http://localhost:8899"
            ;;
        prod-down)
            check_docker
            print_info "Stopping FastCP production mode..."
            $(compose_cmd) -f $PROD_COMPOSE_FILE down "$@"
            print_success "FastCP production mode stopped!"
            ;;
        clean)
            check_docker
            print_warning "This will remove all containers and volumes. Are you sure? (y/N)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                print_info "Cleaning up Docker resources..."
                $(compose_cmd) -f $COMPOSE_FILE down -v --remove-orphans
                $(compose_cmd) -f $PROD_COMPOSE_FILE down -v --remove-orphans
                docker system prune -f
                print_success "Cleanup completed!"
            else
                print_info "Cleanup cancelled."
            fi
            ;;
        -h|--help|help|"")
            usage
            ;;
        *)
            print_error "Unknown command: $cmd"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
