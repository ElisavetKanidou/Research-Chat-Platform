# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy application code
COPY . .

# Create entrypoint script inline to ensure proper line endings
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Create uploads directories if they don'\''t exist' >> /entrypoint.sh && \
    echo 'mkdir -p /app/uploads/reference_papers' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Set proper permissions (777 to allow any user to write)' >> /entrypoint.sh && \
    echo 'chmod -R 777 /app/uploads' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Execute the main command' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Create uploads directory with subdirectories
RUN mkdir -p uploads/reference_papers \
    && chmod -R 777 uploads

# Expose port 8080 (avoiding conflicts)
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/v1/health')" || exit 1

# Use entrypoint to setup permissions before starting
ENTRYPOINT ["/entrypoint.sh"]

# Start command with multiple workers for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
