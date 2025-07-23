# FastAPI GraphQL Blog API

A tutorial project demonstrating how to build a GraphQL API with FastAPI, SQLAlchemy, and PostgreSQL for a simple blog system.

## Quick Start

### Prerequisites
- Python 3.x
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Setup Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Start database and services
docker-compose up -d

# Run database migrations
docker-compose run app alembic upgrade head

# Start the application (if not using docker-compose)
uvicorn main:app --reload
```

### Verification
- GraphQL Playground: http://localhost:8000/graphql
- PgAdmin: http://localhost:5050
- API: http://localhost:8000

## Architecture

This is a simple layered architecture following FastAPI conventions:

```
├── main.py           # FastAPI app, GraphQL schema, queries & mutations
├── models.py         # SQLAlchemy database models
├── schemas.py        # Pydantic schemas & Graphene types
├── db_conf.py        # Database configuration & session
├── alembic/          # Database migration files
├── docker-compose.yml # Multi-service Docker setup
└── Dockerfile        # Application container
```

**Pattern**: Simple MVC-like structure with GraphQL layer
**Database**: PostgreSQL with SQLAlchemy ORM
**Migrations**: Alembic for schema versioning

## Technology Stack

### Core Framework
- **FastAPI 0.66.0** - Web framework
- **Starlette 0.14.2** - ASGI foundation
- **Uvicorn 0.14.0** - ASGI server

### GraphQL
- **Graphene 2.1.8** - GraphQL library
- **Graphene-SQLAlchemy 2.3.0** - SQLAlchemy integration
- **GraphQL-Core 2.3.2** - GraphQL implementation

### Database
- **SQLAlchemy 1.4.20** - ORM
- **Alembic 1.6.5** - Migration tool
- **Psycopg2 2.9.1** - PostgreSQL adapter
- **PostgreSQL** - Database (via Docker)

### Data Validation
- **Pydantic 1.8.2** - Data validation

### Development
- **Black 21.6b0** - Code formatting
- **Python-dotenv 0.18.0** - Environment variables

### Infrastructure
- **Docker** - Containerization
- **PgAdmin4** - Database administration

## Development

### Key Files
- `main.py:14-49` - GraphQL schema with Query and Mutation classes
- `models.py:7-14` - Post model with SQLAlchemy ORM
- `db_conf.py:16` - Database session factory
- `docker-compose.yml:26-36` - Application service configuration

### Build Commands
```bash
# Format code
black .

# Create new migration
docker-compose run app alembic revision --autogenerate -m "Migration name"

# Apply migrations
docker-compose run app alembic upgrade head

# Build and run with Docker
docker-compose up --build
```

### Run Commands
```bash
# Development (local)
uvicorn main:app --reload

# Production (Docker)
docker-compose up -d

# Database only
docker-compose up -d db
```

### Common Workflows
1. **Add new field to Post model** → Update `models.py` → Generate migration → Apply migration
2. **Add new GraphQL field** → Update `PostModel` in `schemas.py` → Test in GraphQL playground
3. **Add new mutation** → Create mutation class in `main.py` → Add to `PostMutations`

## Features

### Core Domain
- **Post Entity** (`models.py:7-14`): Blog posts with title, author, content, timestamp
- **CRUD Operations**: Create posts via GraphQL mutations, query all/by ID

### GraphQL API
- **Queries**:
  - `allPosts` - Get all blog posts
  - `postById(postId: Int!)` - Get specific post by ID
- **Mutations**:
  - `createNewPost(title: String!, content: String!)` - Create new post
- **Endpoint**: `/graphql` with GraphQL Playground interface

### Database
- **Pattern**: SQLAlchemy ORM with declarative models
- **Migration**: Alembic for schema changes
- **Connection**: PostgreSQL via environment variables

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

**Current Status**: No test framework detected
**Recommendation**: Add pytest for API testing

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
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `alembic upgrade head`
4. Start server: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Troubleshooting

### Common Issues
- **Database connection**: Ensure PostgreSQL is running and environment variables are set
- **Migration errors**: Check `alembic.ini` configuration and database permissions
- **GraphQL schema**: Verify model imports and schema registration in `main.py:49`

### Development Tips
- Use GraphQL Playground at `/graphql` for API testing
- Check logs with `docker-compose logs app`
- Access database via PgAdmin at localhost:5050

## Documentation

- **API Documentation**: GraphQL schema introspection via `/graphql` endpoint
- **Commands**: See `commands.md` for setup and query examples
- **Migration History**: `alembic/versions/` (currently empty - needs initial migration)