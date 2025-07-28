# FastAPI GraphQL Blog API

A tutorial project demonstrating how to build a GraphQL API with FastAPI, SQLAlchemy, and PostgreSQL for a simple blog system.

## Quick Start

### Prerequisites
- Python 3.12+
- uv (modern Python package manager)
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Setup Commands
```bash
# Install dependencies with uv
uv sync

# Start database and services
docker-compose up -d

# Run database migrations
docker-compose run app uv run alembic upgrade head

# Start the application (if not using docker-compose)
uv run uvicorn main:app --reload
```

### Verification
- GraphQL Playground: http://localhost:8000/graphql
- PgAdmin: http://localhost:5050
- API: http://localhost:8000

## Architecture

This is a simple layered architecture following FastAPI conventions:

```
├── main.py             # FastAPI app, GraphQL schema, queries & mutations
├── models.py           # SQLAlchemy database models  
├── schemas.py          # Pydantic schemas & Graphene types
├── db_conf.py          # Database configuration & session
├── graphiql_handler.py # Custom GraphiQL interface handler
├── alembic/            # Database migration files
├── docker-compose.yml  # Multi-service Docker setup
├── Dockerfile          # Application container
├── pyproject.toml      # Modern Python project configuration
├── uv.lock             # Dependency lockfile
└── requirements.txt    # Legacy pip compatibility
```

**Pattern**: Simple MVC-like structure with GraphQL layer
**Database**: PostgreSQL with SQLAlchemy 2.0 ORM
**Migrations**: Alembic for schema versioning
**GraphQL**: Custom GraphiQL handler with reliable CDN URLs
**Package Manager**: uv for fast dependency resolution and management

## Technology Stack

### Core Framework
- **FastAPI 0.116.1** - Web framework
- **Starlette 0.47.2** - ASGI foundation
- **Uvicorn 0.35.0** - ASGI server

### GraphQL
- **Graphene 3.4.3** - GraphQL library
- **Graphene-SQLAlchemy 3.0.0rc2** - SQLAlchemy integration
- **GraphQL-Core 3.2.6** - GraphQL implementation
- **Starlette-Graphene3 0.6.0** - FastAPI GraphQL integration

### Database
- **SQLAlchemy 2.0.41** - ORM with modern syntax
- **Alembic 1.16.4** - Migration tool
- **Psycopg 3.2.9** - PostgreSQL adapter (modern version)
- **PostgreSQL** - Database (via Docker)

### Data Validation
- **Pydantic 2.11.7** - Data validation

### Development
- **Black 25.1.0** - Code formatting
- **Python-dotenv 1.1.1** - Environment variables
- **uv** - Modern Python package manager

### Testing
- **Pytest 8.4.1** - Testing framework
- **Pytest-cov 6.2.1** - Coverage reporting
- **HTTPX 0.28.1** - HTTP client for API testing
- **Factory-boy 3.3.3** - Test data generation

### Infrastructure
- **Docker** - Containerization with uv integration
- **PgAdmin4** - Database administration

## Development

### Key Files
- `main.py` - GraphQL schema with Query and Mutation classes, FastAPI app
- `models.py` - Post model with SQLAlchemy 2.0 ORM syntax
- `schemas.py` - Graphene types and Pydantic schemas
- `db_conf.py` - Database session factory
- `graphiql_handler.py` - Custom GraphiQL interface with reliable CDN URLs
- `docker-compose.yml` - Multi-service Docker configuration
- `pyproject.toml` - Modern Python project configuration with dependencies
- `uv.lock` - Dependency lockfile for reproducible environments

### Build Commands
```bash
# Format code
uv run black .

# Run tests (includes coverage automatically)
uv run pytest

# Create new migration
docker-compose run app uv run alembic revision --autogenerate -m "Migration name"

# Apply migrations
docker-compose run app uv run alembic upgrade head

# Build and run with Docker
docker-compose up --build
```

### Run Commands
```bash
# Development (local)
uv run uvicorn main:app --reload

# Production (Docker)
docker-compose up -d

# Database only
docker-compose up -d db
```

### Common Workflows
1. **Add new field to Post model** → Update `models.py` → Generate migration → Apply migration → Run tests
2. **Add new GraphQL field** → Update `PostModel` in `schemas.py` → Add tests → Test in GraphQL playground
3. **Add new mutation** → Create mutation class in `main.py` → Add to `PostMutations` → Write tests
4. **Update dependencies** → Use `uv add package==version` or `uv remove package` → Run tests → Rebuild Docker container
5. **Run full test suite** → `uv run pytest` → Verify 99%+ coverage

## Features

### Core Domain
- **Post Entity** (`models.py`): Blog posts with title, author, content, timestamp
- **CRUD Operations**: Create posts via GraphQL mutations, query all/by ID
- **Modern ORM**: SQLAlchemy 2.0 with Mapped types and DeclarativeBase

### GraphQL API
- **Queries**:
  - `allPosts` - Get all blog posts
  - `postById(postId: Int!)` - Get specific post by ID
- **Mutations**:
  - `createNewPost(title: String!, content: String!)` - Create new post
- **Endpoint**: `/graphql` with custom GraphiQL interface
- **Integration**: Starlette-Graphene3 for FastAPI mounting

### Database
- **Pattern**: SQLAlchemy 2.0 ORM with modern declarative syntax
- **Migration**: Alembic for schema changes with initial migration generated
- **Connection**: PostgreSQL via Psycopg 3.x with environment variables

## Infrastructure Services

```yaml
# docker-compose.yml services:
db:5432          # PostgreSQL database
pgadmin:5050     # Database admin interface  
app:8000         # FastAPI GraphQL application
```

### Service Dependencies
- `app` depends on `db` (PostgreSQL)
- `pgadmin` depends on `db` for database management

### Environment Variables
Required in `.env` file:
- `DATABASE_URL` - PostgreSQL connection string
- `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database credentials
- `PGADMIN_EMAIL`, `PGADMIN_PASSWORD` - PgAdmin credentials

## Testing

**Framework**: pytest with comprehensive test suite
**Coverage**: 99% code coverage across all modules
**Test Types**: Unit tests, integration tests, GraphQL API tests

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_graphql_queries.py  # GraphQL query endpoint tests
├── test_graphql_mutations.py # GraphQL mutation endpoint tests
├── test_models.py           # SQLAlchemy model tests
└── factories.py             # Test data factories using factory-boy
```

### Running Tests
```bash
# Run all tests (includes coverage automatically)
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_graphql_queries.py

# Run only fast tests (skip slow tests)
uv run pytest -m "not slow"

# Override to show only terminal coverage (no HTML)
uv run pytest --cov-report=term-missing --cov-report=

# View HTML coverage report (generated automatically)
open htmlcov/index.html
```

### Test Database
- **Type**: SQLite in-memory database for isolation
- **Isolation**: Each test runs in its own transaction with automatic rollback
- **Fixtures**: Comprehensive fixture setup for database sessions and test client
- **Factories**: factory-boy integration for generating realistic test data

### Test Coverage
- **GraphQL Queries**: Tests for `allPosts` and `postById` with various scenarios
- **GraphQL Mutations**: Tests for `createNewPost` with validation and edge cases
- **Model Tests**: SQLAlchemy model functionality, CRUD operations, and constraints
- **Error Handling**: GraphQL syntax errors, validation errors, and edge cases
- **Database Integration**: Transaction handling, data persistence, and cleanup

### Sample GraphQL Queries

Create a post:
```graphql
mutation CreateNewPost {
  createNewPost(title: "new title1", content: "new content") {
    ok
  }
}
```

Query all posts:
```graphql
query {
  allPosts {
    title
  }
}
```

Query specific post:
```graphql
query {
  postById(postId: 2) {
    id
    title
    content
  }
}
```

## Deployment

### Docker Deployment
```bash
# Full stack deployment
docker-compose up -d

# Apply migrations in production
docker-compose run app alembic upgrade head
```

### Manual Deployment
1. Set environment variables
2. Install dependencies: `uv sync`
3. Run migrations: `uv run alembic upgrade head`
4. Start server: `uv run uvicorn main:app --host 0.0.0.0 --port 8000`

## Troubleshooting

### Common Issues
- **Database connection**: Ensure PostgreSQL is running and environment variables are set
- **Migration errors**: Check `alembic.ini` configuration and database permissions
- **GraphQL schema**: Verify model imports and schema registration in `main.py`
- **GraphiQL loading**: Custom handler fixes CDN issues from GraphiQL 4.0.0 migration
- **Dependencies**: Use uv commands for all package management to ensure consistency

### Development Tips
- Use custom GraphiQL interface at `/graphql` for API testing
- Check logs with `docker-compose logs app`
- Access database via PgAdmin at localhost:5050
- Docker healthchecks ensure reliable service startup sequence

## Recent Updates

### Modernization (2025)
- **Python**: Upgraded from 3.9 to 3.12+
- **Package Manager**: Migrated from Pipenv to uv for faster dependency resolution
- **FastAPI**: Updated to 0.116.1 with latest dependencies
- **SQLAlchemy**: Migrated to 2.0 syntax with Mapped types
- **GraphQL**: Upgraded to Graphene 3.4.3 with starlette-graphene3
- **PostgreSQL**: Migrated from psycopg2 to psycopg3
- **GraphiQL**: Custom handler with reliable jsDelivr CDN URLs
- **Docker**: Optimized for uv with cache mounts and layered builds

## Documentation

- **API Documentation**: GraphQL schema introspection via `/graphql` endpoint
- **Migration History**: Initial migration generated for Post model schema