"""
Test configuration and shared fixtures
"""
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from db_conf import Base
from main import app


# Test database setup
@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine using SQLite in memory"""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False}
    )
    
    try:
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        # Clean up database after tests
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create test database session with rollback after each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    
    # Start a connection and transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Create session bound to the connection
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        # Clean up after test completes
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def test_client(test_db_session) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with database dependency override"""
    
    # Store original db session
    import main
    original_db = main.db
    
    # Replace with test session
    main.db = test_db_session
    
    with TestClient(app) as client:
        yield client
    
    # Restore original session
    main.db = original_db


@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        "title": "Test Post Title",
        "content": "This is test post content for testing purposes."
    }


@pytest.fixture
def create_sample_post(test_db_session):
    """Factory fixture to create sample posts in test database"""
    def _create_post(title="Sample Post", content="Sample content", author=None):
        post = models.Post(
            title=title,
            content=content,
            author=author
        )
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        return post
    
    return _create_post