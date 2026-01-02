#!/bin/bash

# Build script for frontend applications
set -e

echo "Building frontend applications..."

# Build Staff App
echo "Building Staff App..."
cd frontend/staff
npm install
npm run build
cd ../..

# Build Display App
echo "Building Display App..."
cd frontend/display
npm install
npm run build
cd ../..

# Build Client App
echo "Building Client App..."
cd frontend/client
npm install
npm run build
cd ../..

echo "All frontend applications built successfully!"
echo ""
echo "Build outputs:"
echo "  - Staff: frontend/staff/dist"
echo "  - Display: frontend/display/dist"
echo "  - Client: frontend/client/dist"
