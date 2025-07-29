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


class TestUpdatePostMutation:
    """Test updatePost GraphQL mutation"""
    
    def test_update_post_success(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test successful post update"""
        # Create a sample post
        post = create_sample_post(title="Original Title", content="Original content")
        
        mutation = f"""
        mutation {{
            updatePost(id: {post.id}, title: "Updated Title", content: "Updated content") {{
                ok
                error
                post {{
                    id
                    title
                    content
                    author
                }}
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["updatePost"]["ok"] is True
        assert data["data"]["updatePost"]["error"] is None
        assert data["data"]["updatePost"]["post"]["title"] == "Updated Title"
        assert data["data"]["updatePost"]["post"]["content"] == "Updated content"
        
        # Verify update in database
        updated_post = test_db_session.query(models.Post).filter(models.Post.id == post.id).first()
        assert updated_post.title == "Updated Title"
        assert updated_post.content == "Updated content"
    
    def test_update_post_partial_fields(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test updating only some fields"""
        post = create_sample_post(title="Original Title", content="Original content", author="Original Author")
        
        # Update only title
        mutation = f"""
        mutation {{
            updatePost(id: {post.id}, title: "Only Title Updated") {{
                ok
                error
                post {{
                    title
                    content
                    author
                }}
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updatePost"]["ok"] is True
        assert data["data"]["updatePost"]["error"] is None
        assert data["data"]["updatePost"]["post"]["title"] == "Only Title Updated"
        assert data["data"]["updatePost"]["post"]["content"] == "Original content"  # Unchanged
        assert data["data"]["updatePost"]["post"]["author"] == "Original Author"   # Unchanged
    
    def test_update_post_with_author(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test updating post with author field"""
        post = create_sample_post(title="Test Post", content="Test content")
        
        mutation = f"""
        mutation {{
            updatePost(id: {post.id}, author: "New Author") {{
                ok
                error
                post {{
                    author
                }}
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updatePost"]["ok"] is True
        assert data["data"]["updatePost"]["error"] is None
        assert data["data"]["updatePost"]["post"]["author"] == "New Author"
    
    def test_update_post_nonexistent_id(self, test_client: TestClient):
        """Test updating post with non-existent ID"""
        mutation = """
        mutation {
            updatePost(id: 99999, title: "Updated Title") {
                ok
                error
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updatePost"]["ok"] is False
        assert "not found" in data["data"]["updatePost"]["error"]
    
    def test_update_post_empty_update(self, test_client: TestClient, create_sample_post):
        """Test update mutation with no fields to update"""
        post = create_sample_post(title="Original Title", content="Original content")
        
        mutation = f"""
        mutation {{
            updatePost(id: {post.id}) {{
                ok
                error
                post {{
                    title
                    content
                }}
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updatePost"]["ok"] is True
        assert data["data"]["updatePost"]["error"] is None
        # Fields should remain unchanged
        assert data["data"]["updatePost"]["post"]["title"] == "Original Title"
        assert data["data"]["updatePost"]["post"]["content"] == "Original content"
    
    def test_update_post_missing_required_id(self, test_client: TestClient):
        """Test updatePost mutation without required id parameter"""
        mutation = """
        mutation {
            updatePost(title: "New Title")
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0


class TestDeletePostMutation:
    """Test deletePost GraphQL mutation"""
    
    def test_delete_post_success(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test successful post deletion"""
        post = create_sample_post(title="To be deleted", content="This will be deleted")
        post_id = post.id
        
        mutation = f"""
        mutation {{
            deletePost(id: {post_id}) {{
                ok
                error
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deletePost"]["ok"] is True
        assert data["data"]["deletePost"]["error"] is None
        
        # Verify deletion in database
        deleted_post = test_db_session.query(models.Post).filter(models.Post.id == post_id).first()
        assert deleted_post is None
    
    def test_delete_post_nonexistent_id(self, test_client: TestClient):
        """Test deleting post with non-existent ID"""
        mutation = """
        mutation {
            deletePost(id: 99999) {
                ok
                error
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deletePost"]["ok"] is False
        assert "not found" in data["data"]["deletePost"]["error"]
    
    def test_delete_post_missing_required_id(self, test_client: TestClient):
        """Test deletePost mutation without required id parameter"""
        mutation = """
        mutation {
            deletePost
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_delete_post_selective_deletion(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test that deleting one post doesn't affect others"""
        post1 = create_sample_post(title="Post 1", content="Content 1")
        post2 = create_sample_post(title="Post 2", content="Content 2")
        post3 = create_sample_post(title="Post 3", content="Content 3")
        
        # Delete only post2, leaving post1 and post3
        mutation = f"""
        mutation {{
            deletePost(id: {post2.id}) {{
                ok
                error
            }}
        }}
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deletePost"]["ok"] is True
        assert data["data"]["deletePost"]["error"] is None
        
        # Verify only post2 is deleted, post1 and post3 remain
        remaining_posts = test_db_session.query(models.Post).all()
        assert len(remaining_posts) == 2
        remaining_ids = [post.id for post in remaining_posts]
        assert post1.id in remaining_ids
        assert post3.id in remaining_ids
        assert post2.id not in remaining_ids