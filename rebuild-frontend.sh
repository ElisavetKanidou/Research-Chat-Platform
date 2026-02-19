#!/bin/bash

# Stop and remove containers
echo "🛑 Stopping containers..."
docker compose down

# Remove old frontend image to force rebuild
echo "🗑️  Removing old frontend image..."
docker rmi research-chat-ai-frontend 2>/dev/null || true

# Rebuild frontend (without cache)
echo "🔨 Rebuilding frontend..."
docker compose build --no-cache frontend

# Start all services
echo "🚀 Starting services..."
docker compose up -d

# Show logs
echo "📝 Showing logs..."
docker compose logs -f
