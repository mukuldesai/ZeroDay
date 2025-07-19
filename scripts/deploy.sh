#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

ENVIRONMENT="${1:-staging}"
DEPLOY_TYPE="${2:-standard}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking deployment dependencies..."
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v kubectl &> /dev/null; then
        missing_deps+=("kubectl")
    fi
    
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "All dependencies available"
}

validate_environment() {
    log_info "Validating environment: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        "development"|"staging"|"production")
            log_success "Valid environment: $ENVIRONMENT"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

check_environment_variables() {
    log_info "Checking environment variables..."
    
    local required_vars=(
        "DATABASE_URL"
        "SECRET_KEY"
        "OPENAI_API_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    log_success "Environment variables validated"
}

run_tests() {
    log_info "Running test suite..."
    
    cd "$PROJECT_ROOT"
    
    if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
        log_info "Running Python tests..."
        python3 -m pytest tests/ -v --tb=short
        if [ $? -ne 0 ]; then
            log_error "Python tests failed"
            exit 1
        fi
    fi
    
    if [ -f "frontend/package.json" ]; then
        log_info "Running frontend tests..."
        cd frontend
        npm test -- --watchAll=false --coverage=false
        if [ $? -ne 0 ]; then
            log_error "Frontend tests failed"
            exit 1
        fi
        cd ..
    fi
    
    log_success "All tests passed"
}

build_backend() {
    log_info "Building backend..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$DEPLOY_TYPE" = "docker" ]; then
        log_info "Building Docker image for backend..."
        docker build -t zeroday-backend:$ENVIRONMENT -f Dockerfile.backend .
        if [ $? -ne 0 ]; then
            log_error "Backend Docker build failed"
            exit 1
        fi
        log_success "Backend Docker image built"
    else
        log_info "Installing Python dependencies..."
        python3 -m pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            log_error "Python dependency installation failed"
            exit 1
        fi
        log_success "Backend dependencies installed"
    fi
}

build_frontend() {
    log_info "Building frontend..."
    
    cd "$PROJECT_ROOT/frontend"
    
    log_info "Installing Node.js dependencies..."
    npm ci
    if [ $? -ne 0 ]; then
        log_error "Node.js dependency installation failed"
        exit 1
    fi
    
    log_info "Building Next.js application..."
    npm run build
    if [ $? -ne 0 ]; then
        log_error "Frontend build failed"
        exit 1
    fi
    
    if [ "$DEPLOY_TYPE" = "docker" ]; then
        log_info "Building Docker image for frontend..."
        docker build -t zeroday-frontend:$ENVIRONMENT -f Dockerfile.frontend .
        if [ $? -ne 0 ]; then
            log_error "Frontend Docker build failed"
            exit 1
        fi
        log_success "Frontend Docker image built"
    fi
    
    cd "$PROJECT_ROOT"
    log_success "Frontend build completed"
}

setup_database() {
    log_info "Setting up database..."
    
    cd "$PROJECT_ROOT"
    
    python3 database/setup.py
    if [ $? -ne 0 ]; then
        log_error "Database setup failed"
        exit 1
    fi
    
    log_success "Database setup completed"
}

deploy_to_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    local k8s_dir="$PROJECT_ROOT/k8s"
    
    if [ ! -d "$k8s_dir" ]; then
        log_error "Kubernetes manifests directory not found: $k8s_dir"
        exit 1
    fi
    
    kubectl config current-context
    log_info "Deploying to cluster: $(kubectl config current-context)"
    
    log_info "Creating namespace if not exists..."
    kubectl create namespace zeroday-$ENVIRONMENT --dry-run=client -o yaml | kubectl apply -f -
    
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f "$k8s_dir/$ENVIRONMENT/" -n zeroday-$ENVIRONMENT
    if [ $? -ne 0 ]; then
        log_error "Kubernetes deployment failed"
        exit 1
    fi
    
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment --all -n zeroday-$ENVIRONMENT
    if [ $? -ne 0 ]; then
        log_error "Deployment readiness check failed"
        exit 1
    fi
    
    log_success "Kubernetes deployment completed"
}

deploy_to_vercel() {
    log_info "Deploying frontend to Vercel..."
    
    cd "$PROJECT_ROOT/frontend"
    
    if ! command -v vercel &> /dev/null; then
        log_info "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    if [ "$ENVIRONMENT" = "production" ]; then
        vercel --prod --confirm
    else
        vercel --confirm
    fi
    
    if [ $? -ne 0 ]; then
        log_error "Vercel deployment failed"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    log_success "Vercel deployment completed"
}

deploy_to_railway() {
    log_info "Deploying backend to Railway..."
    
    cd "$PROJECT_ROOT"
    
    if ! command -v railway &> /dev/null; then
        log_info "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    railway login
    railway up
    
    if [ $? -ne 0 ]; then
        log_error "Railway deployment failed"
        exit 1
    fi
    
    log_success "Railway deployment completed"
}

deploy_standard() {
    log_info "Starting standard deployment..."
    
    check_dependencies
    validate_environment
    check_environment_variables
    run_tests
    build_backend
    build_frontend
    setup_database
    
    case $ENVIRONMENT in
        "development")
            log_info "Development deployment - starting local services"
            ;;
        "staging"|"production")
            deploy_to_vercel
            deploy_to_railway
            ;;
    esac
    
    log_success "Standard deployment completed"
}

deploy_docker() {
    log_info "Starting Docker deployment..."
    
    check_dependencies
    validate_environment
    check_environment_variables
    run_tests
    build_backend
    build_frontend
    
    log_info "Starting Docker Compose services..."
    docker-compose -f docker-compose.$ENVIRONMENT.yml up -d
    
    if [ $? -ne 0 ]; then
        log_error "Docker Compose deployment failed"
        exit 1
    fi
    
    log_success "Docker deployment completed"
}

deploy_kubernetes() {
    log_info "Starting Kubernetes deployment..."
    
    check_dependencies
    validate_environment
    check_environment_variables
    run_tests
    build_backend
    build_frontend
    deploy_to_kubernetes
    
    log_success "Kubernetes deployment completed"
}

health_check() {
    log_info "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        if curl -f -s http://localhost:8000/api/health > /dev/null 2>&1; then
            log_success "Backend health check passed"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Backend health check failed after $max_attempts attempts"
            exit 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_success "Health check completed"
}

rollback() {
    log_info "Performing rollback..."
    
    case $DEPLOY_TYPE in
        "kubernetes")
            kubectl rollout undo deployment/zeroday-backend -n zeroday-$ENVIRONMENT
            kubectl rollout undo deployment/zeroday-frontend -n zeroday-$ENVIRONMENT
            ;;
        "docker")
            docker-compose -f docker-compose.$ENVIRONMENT.yml down
            docker-compose -f docker-compose.$ENVIRONMENT.yml up -d
            ;;
        *)
            log_warning "Rollback not implemented for deployment type: $DEPLOY_TYPE"
            ;;
    esac
    
    log_success "Rollback completed"
}

show_deployment_info() {
    echo ""
    echo "================================================================"
    echo "🚀 ZeroDay Deployment Complete!"
    echo "================================================================"
    echo "Environment: $ENVIRONMENT"
    echo "Deployment Type: $DEPLOY_TYPE"
    echo "Timestamp: $(date)"
    echo ""
    echo "Services:"
    case $DEPLOY_TYPE in
        "standard")
            if [ "$ENVIRONMENT" = "development" ]; then
                echo "  • Backend: http://localhost:8000"
                echo "  • Frontend: http://localhost:3000"
            else
                echo "  • Frontend: Deployed to Vercel"
                echo "  • Backend: Deployed to Railway"
            fi
            ;;
        "docker")
            echo "  • Backend: http://localhost:8000"
            echo "  • Frontend: http://localhost:3000"
            echo "  • Database: localhost:5432"
            ;;
        "kubernetes")
            echo "  • Check services: kubectl get svc -n zeroday-$ENVIRONMENT"
            echo "  • Check pods: kubectl get pods -n zeroday-$ENVIRONMENT"
            ;;
    esac
    echo ""
    echo "Health Check: curl http://localhost:8000/api/health"
    echo "Logs: View application logs for monitoring"
    echo "================================================================"
}

main() {
    log_info "ZeroDay Deployment Script"
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment Type: $DEPLOY_TYPE"
    
    case $DEPLOY_TYPE in
        "standard")
            deploy_standard
            ;;
        "docker")
            deploy_docker
            ;;
        "kubernetes")
            deploy_kubernetes
            ;;
        "rollback")
            rollback
            exit 0
            ;;
        *)
            log_error "Invalid deployment type: $DEPLOY_TYPE"
            log_error "Valid types: standard, docker, kubernetes, rollback"
            exit 1
            ;;
    esac
    
    health_check
    show_deployment_info
}

cleanup() {
    log_info "Cleaning up temporary files..."
    
    find "$PROJECT_ROOT" -name "*.pyc" -delete
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    if [ -d "$PROJECT_ROOT/frontend/.next" ]; then
        rm -rf "$PROJECT_ROOT/frontend/.next"
    fi
    
    log_success "Cleanup completed"
}

show_usage() {
    echo "Usage: $0 [environment] [deploy_type]"
    echo ""
    echo "Environments:"
    echo "  development  - Local development deployment"
    echo "  staging      - Staging environment deployment"
    echo "  production   - Production environment deployment"
    echo ""
    echo "Deployment Types:"
    echo "  standard     - Standard deployment (Vercel + Railway)"
    echo "  docker       - Docker Compose deployment"
    echo "  kubernetes   - Kubernetes cluster deployment"
    echo "  rollback     - Rollback to previous version"
    echo ""
    echo "Examples:"
    echo "  $0 development standard"
    echo "  $0 staging docker"
    echo "  $0 production kubernetes"
    echo "  $0 staging rollback"
    echo ""
    echo "Environment Variables Required:"
    echo "  DATABASE_URL     - Database connection string"
    echo "  SECRET_KEY       - Application secret key"
    echo "  OPENAI_API_KEY   - OpenAI API key"
    echo "  ANTHROPIC_API_KEY - Anthropic API key (optional)"
}

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_usage
    exit 0
fi

if [ $# -eq 0 ]; then
    log_warning "No arguments provided, using defaults"
    log_info "Use --help for usage information"
fi

trap cleanup EXIT

main "$@"