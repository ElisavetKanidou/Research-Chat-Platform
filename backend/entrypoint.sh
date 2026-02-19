#!/bin/bash
set -e

# Create uploads directories if they don't exist
mkdir -p /app/uploads/reference_papers

# Set proper permissions (777 to allow any user to write)
chmod -R 777 /app/uploads

# Execute the main command
exec "$@"
