"""
Test GraphQL mutations
"""
import pytest
from fastapi.testclient import TestClient

import models


class TestGraphQLMutations:
    """Test GraphQL mutation operations"""
    
    def test_create_new_post_success(self, test_client: TestClient, test_db_session):
        """Test successful post creation via createNewPost mutation"""
        mutation = """
        mutation {
            createNewPost(title: "Test Post", content: "Test content") {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["createNewPost"]["ok"] is True
        assert "errors" not in data
        
        # Verify post was actually created in database
        posts = test_db_session.query(models.Post).all()
        assert len(posts) == 1
        assert posts[0].title == "Test Post"
        assert posts[0].content == "Test content"
        assert posts[0].time_created is not None
    
    def test_create_new_post_with_special_characters(self, test_client: TestClient, test_db_session):
        """Test post creation with special characters and unicode"""
        mutation = """
        mutation {
            createNewPost(
                title: "Post with émojis 🚀 and symbols !@#$%"
                content: "Content with newlines\\nand quotes 'single' and \\"double\\""
            ) {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createNewPost"]["ok"] is True
        
        # Verify special characters are preserved
        post = test_db_session.query(models.Post).first()
        assert "🚀" in post.title
        assert "émojis" in post.title
        assert "newlines\nand" in post.content  # Actual newline, not escaped
    
    def test_create_new_post_missing_title(self, test_client: TestClient):
        """Test createNewPost mutation without required title parameter"""
        mutation = """
        mutation {
            createNewPost(content: "Content without title") {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        # Should mention missing required argument
        error_message = str(data["errors"][0])
        assert "title" in error_message.lower()
    
    def test_create_new_post_missing_content(self, test_client: TestClient):
        """Test createNewPost mutation without required content parameter"""
        mutation = """
        mutation {
            createNewPost(title: "Title without content") {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        # Should mention missing required argument
        error_message = str(data["errors"][0])
        assert "content" in error_message.lower()
    
    def test_create_new_post_empty_strings(self, test_client: TestClient, test_db_session):
        """Test createNewPost mutation with empty strings"""
        mutation = """
        mutation {
            createNewPost(title: "", content: "") {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createNewPost"]["ok"] is True
        
        # Verify empty strings are stored
        post = test_db_session.query(models.Post).first()
        assert post.title == ""
        assert post.content == ""
    
    def test_create_new_post_very_long_content(self, test_client: TestClient, test_db_session):
        """Test createNewPost mutation with very long content"""
        long_content = "Very long content " * 100  # Create long string
        
        mutation = f"""
        mutation {{
            createNewPost(
                title: "Long Content Post"
                content: "{long_content}"
            ) {{
                ok
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createNewPost"]["ok"] is True
        
        # Verify long content is stored
        post = test_db_session.query(models.Post).first()
        assert len(post.content) > 1000
        assert "Very long content" in post.content
    
    def test_create_multiple_posts(self, test_client: TestClient, test_db_session):
        """Test creating multiple posts in sequence"""
        posts_data = [
            ("First Post", "First content"),
            ("Second Post", "Second content"),
            ("Third Post", "Third content")
        ]
        
        for title, content in posts_data:
            mutation = f"""
            mutation {{
                createNewPost(title: "{title}", content: "{content}") {{
                    ok
                }}
            }}
            """
            
            response = test_client.post("/graphql/", json={"query": mutation})
            assert response.status_code == 200
            assert response.json()["data"]["createNewPost"]["ok"] is True
        
        # Verify all posts were created
        posts = test_db_session.query(models.Post).all()
        assert len(posts) == 3
        
        titles = [post.title for post in posts]
        assert "First Post" in titles
        assert "Second Post" in titles
        assert "Third Post" in titles
    
    def test_invalid_mutation_syntax(self, test_client: TestClient):
        """Test invalid GraphQL mutation syntax"""
        invalid_mutation = """
        mutation {
            createNewPost(title: "Test" content: "Missing comma") {
                ok
            }
        """
        
        response = test_client.post("/graphql/", json={"query": invalid_mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_nonexistent_mutation(self, test_client: TestClient):
        """Test calling non-existent mutation"""
        mutation = """
        mutation {
            nonExistentMutation(title: "Test") {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0