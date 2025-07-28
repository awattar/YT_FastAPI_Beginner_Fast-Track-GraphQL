"""
Test GraphQL queries
"""
import pytest
from fastapi.testclient import TestClient

from tests.factories import create_post_factory


class TestGraphQLQueries:
    """Test GraphQL query operations"""
    
    def test_all_posts_empty_database(self, test_client: TestClient):
        """Test allPosts query with empty database"""
        query = """
        query {
            allPosts {
                id
                title
                content
                author
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["allPosts"] == []
        assert "errors" not in data
    
    def test_all_posts_with_data(self, test_client: TestClient, test_db_session):
        """Test allPosts query with sample data"""
        # Create test posts using factory
        PostFactory = create_post_factory(test_db_session)
        post1 = PostFactory(title="First Post", content="First content")
        post2 = PostFactory(title="Second Post", content="Second content")
        
        query = """
        query {
            allPosts {
                id
                title
                content
                author
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]["allPosts"]) == 2
        
        # Check posts are returned (order may vary)
        titles = [post["title"] for post in data["data"]["allPosts"]]
        assert "First Post" in titles
        assert "Second Post" in titles
    
    def test_post_by_id_valid_id(self, test_client: TestClient, test_db_session):
        """Test postById query with valid ID"""
        # Create test post
        PostFactory = create_post_factory(test_db_session)
        test_post = PostFactory(
            title="Test Post by ID", 
            content="Test content for ID query"
        )
        
        query = """
        query {
            postById(postId: %d) {
                id
                title
                content
                author
            }
        }
        """ % test_post.id
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert int(data["data"]["postById"]["id"]) == test_post.id  # GraphQL returns string
        assert data["data"]["postById"]["title"] == "Test Post by ID"
        assert data["data"]["postById"]["content"] == "Test content for ID query"
    
    def test_post_by_id_invalid_id(self, test_client: TestClient):
        """Test postById query with non-existent ID"""
        query = """
        query {
            postById(postId: 99999) {
                id
                title
                content
                author
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["postById"] is None
        # No errors should be present for null results
        assert "errors" not in data
    
    def test_post_by_id_missing_required_parameter(self, test_client: TestClient):
        """Test postById query without required postId parameter"""
        query = """
        query {
            postById {
                id
                title
                content
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        # GraphQL validation error should be present
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_invalid_graphql_syntax(self, test_client: TestClient):
        """Test invalid GraphQL syntax handling"""
        invalid_query = """
        query {
            allPosts {
                id
                title
                content
                # Missing closing brace
        """
        
        response = test_client.post("/graphql/", json={"query": invalid_query})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_nonexistent_field(self, test_client: TestClient):
        """Test query with non-existent field"""
        query = """
        query {
            allPosts {
                id
                title
                nonExistentField
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0