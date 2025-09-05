# README.md
# Research Platform Backend

A comprehensive academic research management platform with AI assistance, built with FastAPI.

## Features

- **User Management**: Authentication, authorization, and user profiles
- **Paper Management**: Full CRUD operations for research papers with sections
- **AI Chat Assistant**: Context-aware research assistance using OpenAI
- **Collaboration**: Multi-user collaboration on research papers
- **Analytics**: Research productivity tracking and insights
- **File Management**: Upload and manage research documents
- **Real-time Features**: WebSocket support for live collaboration

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Primary database with async support
- **Redis**: Caching and session storage
- **SQLAlchemy**: Database ORM with async support
- **OpenAI**: AI-powered research assistance
- **Celery**: Background task processing
- **Docker**: Containerization and deployment

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd research-platform-backend

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Create an admin user
docker-compose exec api python scripts/create_admin.py

# Access the API
open http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone and setup environment
git clone <repository-url>
cd research-platform-backend

# Run setup script
python scripts/setup_dev.py

# Activate virtual environment
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate  # Windows

# Start PostgreSQL and Redis locally
# Update .env file with your database credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Access the API
open http://localhost:8000/docs
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/research_platform

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
SMTP_HOST=localhost
SMTP_PORT=587
EMAIL_FROM=noreply@yourapp.com
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development Commands

```bash
# Run tests
pytest

# Format code
black .

# Type checking
mypy .

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Create admin user
python scripts/create_admin.py

# Migrate sample data
python scripts/migrate_data.py --migrate
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core utilities (config, exceptions)
│   ├── database/             # Database connection and migrations
│   ├── external/             # External service clients (OpenAI)
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   └── utils/                # Utility functions
├── scripts/                  # Setup and migration scripts
├── requirements/             # Dependency files
└── tests/                    # Test suite
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Papers
- `GET /api/v1/papers/` - List user papers
- `POST /api/v1/papers/` - Create new paper
- `GET /api/v1/papers/{id}` - Get specific paper
- `PATCH /api/v1/papers/{id}` - Update paper
- `DELETE /api/v1/papers/{id}` - Delete paper

### AI Chat
- `POST /api/v1/chat/message` - Send chat message
- `GET /api/v1/chat/history` - Get chat history
- `POST /api/v1/chat/personalization` - Update AI settings

### Analytics
- `GET /api/v1/analytics/overview` - Get analytics overview
- `GET /api/v1/analytics/productivity` - Get productivity metrics

## Frontend Integration

This backend is designed to work with the React frontend. Key integration points:

1. **Authentication**: JWT tokens with automatic refresh
2. **Real-time updates**: WebSocket support for live collaboration
3. **File uploads**: Secure file handling with validation
4. **Error handling**: Standardized error responses
5. **CORS**: Configured for frontend development servers

## Deployment

### Production Deployment

1. **Environment Setup**:
   ```bash
   # Use production requirements
   pip install -r requirements/prod.txt
   
   # Set production environment variables
   export DEBUG=false
   export SECRET_KEY=production-secret-key
   ```

2. **Database Setup**:
   ```bash
   # Run migrations
   alembic upgrade head
   ```

3. **Start Application**:
   ```bash
   # Using Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Production

```bash
# Build production image
docker build -t research-platform-api .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run code quality checks
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review the API examples in `/tests`