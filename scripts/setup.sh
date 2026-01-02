#!/bin/bash

# Setup script for development environment
set -e

echo "Setting up QR Queue System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Create .env file for backend if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
fi

# Start services
echo "Starting Docker services..."
docker-compose up -d db redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# Start backend
echo "Starting backend..."
docker-compose up -d backend

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services running:"
echo "  - Database: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Backend API: http://localhost:8000"
echo ""
echo "To start frontend applications:"
echo "  - Staff: cd frontend/staff && npm install && npm run dev"
echo "  - Display: cd frontend/display && npm install && npm run dev"
echo "  - Client: cd frontend/client && npm install && npm run dev"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"
