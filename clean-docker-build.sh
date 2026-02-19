#!/bin/bash

echo "🧹 Cleaning Docker build artifacts for frontend..."

# Stop and remove frontend container
docker compose stop frontend 2>/dev/null
docker compose rm -f frontend 2>/dev/null

# Remove frontend image
docker rmi research-chat-ai-frontend 2>/dev/null
docker rmi $(docker images -q research-chat-*frontend*) 2>/dev/null

# Prune build cache
docker builder prune -af

# Remove any dangling images
docker image prune -f

echo "✅ Docker cache cleaned!"
echo ""
echo "Now run:"
echo "  docker compose build --no-cache frontend"
echo "  docker compose up -d frontend"
