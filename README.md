# SEO Compass

SEO analysis automation tool that transforms a single URL into a comprehensive SEO strategy report and draft content.

## Architecture

This project follows Clean Architecture principles with the following layers:

- **Domain**: Core business entities and types (`app/domain/`)
- **Application**: Use cases and business logic (`app/application/`)
- **Infrastructure**: External services, database, and frameworks (`app/infrastructure/`)
- **Interfaces**: API endpoints and request/response handling (`app/interfaces/`)

## Tech Stack

- **FastAPI**: Async web framework
- **PostgreSQL**: Database with async SQLAlchemy 2.0
- **Celery + Redis**: Background task processing
- **Pydantic v2**: Data validation and settings
- **Docker**: Containerization for local development

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose

### Setup

1. **Clone and configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

2. **Build and start services**:
   ```bash
   make build && make up
   ```

3. **Run database migrations**:
   ```bash
   make migrate
   ```

4. **Verify installation**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "ok", "app": "seo-compass", "version": "0.1.0"}
   ```

## API Usage

### Submit URL for Analysis

```bash
curl -X POST "http://localhost:8000/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "QUEUED"
}
```

### Check Job Status

```bash
curl "http://localhost:8000/v1/jobs/{job_id}"
```

### Get Analysis Report

```bash
curl "http://localhost:8000/v1/reports/{job_id}"
```

## Development

### Available Commands

```bash
make build    # Build Docker images
make up       # Start all services
make down     # Stop all services
make migrate  # Run database migrations
make test     # Run tests
make lint     # Run linting and type checking
make format   # Format code
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Formatting
black .
```

## Project Structure

```
seo_compass/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── core/                      # Configuration and logging
│   ├── domain/                    # Business entities and types
│   ├── application/usecases/      # Business use cases
│   ├── infrastructure/            # External services and database
│   ├── interfaces/http/           # API endpoints
│   ├── tasks/                     # Celery background tasks
│   └── schemas/                   # Pydantic request/response models
├── tests/                         # Test suite
├── alembic/                       # Database migrations
├── docker-compose.yml             # Local development services
└── pyproject.toml                 # Project configuration
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SERP_API_KEY`: SERP API key for competitor research
- `LLM_API_KEY`: OpenAI or other LLM API key
- `SECRET_KEY`: Application secret key

## Stage 2 Implementation ✅

The current implementation provides:
- ✅ Working FastAPI app with health checks
- ✅ Database models and migrations
- ✅ Celery task processing with 3-second simulation
- ✅ Typed domain entities and use cases
- ✅ Complete API endpoints for analysis workflow
- ✅ Job status tracking (QUEUED → IN_PROGRESS → COMPLETED)
- ✅ Mock data generation for competitors, keywords, and content drafts
- ✅ Comprehensive test suite
- ✅ Error handling and logging

## Testing

```bash
# Run all tests
pytest -v

# Run specific test files
pytest tests/test_health.py -v
pytest tests/test_analyze_flow.py -v

# Run with test runner script
python run_tests.py
```

## Next Steps (Stage 3)

**TODO for Stage 3**:
- Implement real SERP API integration (SerpApi, DataForSEO)
- Add LLM prompt engineering for content generation (OpenAI/Claude)
- Enhance keyword extraction and analysis logic
- Add comprehensive error handling and retry mechanisms
- Implement rate limiting and job queuing
- Add authentication and user management