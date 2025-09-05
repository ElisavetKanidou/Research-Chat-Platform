# scripts/setup_dev.py
# !/usr/bin/env python3
"""
Development environment setup script
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description="Running command"):
    """Run shell command with error handling"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e.stderr}")
        return None


def setup_environment():
    """Setup development environment"""
    print("🚀 Setting up Research Platform Backend Development Environment")

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✓ Python {python_version.major}.{python_version.minor} detected")

    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("\n📦 Creating virtual environment...")
        run_command("python -m venv venv", "Creating virtual environment")

    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"

    # Install dependencies
    run_command(f"{pip_path} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_path} install -r requirements/dev.txt", "Installing dependencies")

    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        print("\n⚙️ Creating .env file...")
        env_content = """# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/research_platform

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379

# OpenAI (optional - will use mock responses if not provided)
OPENAI_API_KEY=your-openai-api-key-here

# Email (optional)
EMAIL_FROM=noreply@yourapp.com
EMAIL_FROM_NAME=Research Platform
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Development settings
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✓ .env file created - please update with your actual values")

    # Create upload directory
    os.makedirs("uploads", exist_ok=True)
    print("✓ Upload directory created")

    # Setup pre-commit hooks
    run_command(f"{python_path} -m pre_commit install", "Setting up pre-commit hooks")

    print("\n🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your database and API keys")
    print("2. Set up PostgreSQL database")
    print("3. Run database migrations: alembic upgrade head")
    print("4. Start the development server: uvicorn app.main:app --reload")


def setup_database():
    """Setup database and run migrations"""
    print("\n🗄️ Setting up database...")

    # Create database if it doesn't exist (PostgreSQL)
    db_commands = [
        "createdb research_platform",
        "alembic upgrade head"
    ]

    for cmd in db_commands:
        run_command(cmd, f"Running: {cmd}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup Research Platform Backend")
    parser.add_argument("--database", action="store_true", help="Setup database and migrations")
    parser.add_argument("--full", action="store_true", help="Full setup including database")

    args = parser.parse_args()

    setup_environment()

    if args.database or args.full:
        setup_database()
