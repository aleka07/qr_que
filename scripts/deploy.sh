#!/bin/bash

# Production deployment script
set -e

echo "Deploying QR Queue System to production..."

# Build frontend applications
./scripts/build_frontend.sh

# Build and start all services with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Services are running:"
echo "  - API: http://api.kaskyralmaty.dev"
echo "  - Staff: http://staff.kaskyralmaty.dev"
echo "  - Display: http://display.kaskyralmaty.dev"
echo "  - Client: http://track.kaskyralmaty.dev"
