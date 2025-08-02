"""
Test GraphQL mutations with Input Object syntax
"""
import pytest
from fastapi.testclient import TestClient

import models


class TestCreatePostMutation:
    """Test GraphQL mutation operations with Input Objects"""
    
    def test_create_new_post_success(self, test_client: TestClient, test_db_session):
        """Test successful post creation via createNewPost mutation with Input Object"""
        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
                post {
                    id
                    title
                    content
                    author
                }
            }
        }
        """
        
        variables = {
            "input": {
                "title": "Test Post",
                "content": "Test content", 
                "author": "Test Author"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["createNewPost"]["ok"] is True
        assert "errors" not in data
        
        # Verify post data in response
        post_data = data["data"]["createNewPost"]["post"]
        assert post_data["title"] == "Test Post"
        assert post_data["content"] == "Test content"
        assert post_data["author"] == "Test Author"
        
        # Verify post was actually created in database
        posts = test_db_session.query(models.Post).all()
        assert len(posts) == 1
        assert posts[0].title == "Test Post"
        assert posts[0].content == "Test content"
        assert posts[0].author == "Test Author"
        assert posts[0].time_created is not None
    
    def test_create_new_post_with_special_characters(self, test_client: TestClient, test_db_session):
        """Test post creation with special characters and unicode"""
        mutation = """
        mutation CreatePostSpecial($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
                post {
                    title
                    content
                    author
                }
            }
        }
        """
        
        variables = {
            "input": {
                "title": "Post with émojis 🚀 and symbols !@#$%",
                "content": "Content with newlines\nand quotes 'single' and \"double\"",
                "author": "Author with émojis 🚀 & symbols !@#"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createNewPost"]["ok"] is True
        
        # Verify special characters are preserved
        post = test_db_session.query(models.Post).first()
        assert "🚀" in post.title
        assert "émojis" in post.title
        assert "newlines\nand" in post.content  # Actual newline, not escaped
        assert "🚀" in post.author
        assert "émojis" in post.author
        assert "'" in post.content and '"' in post.content

    def test_create_new_post_very_long_content(self, test_client: TestClient, test_db_session):
        """Test createNewPost mutation with very long content"""
        long_content = "A" * 5000  # 5k characters
        
        mutation = """
        mutation CreatePostLong($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
            }
        }
        """
        
        variables = {
            "input": {
                "title": "Long Content Post",
                "content": long_content,
                "author": "Long Content Author"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["createNewPost"]["ok"] is True
        
        # Verify long content is stored
        post = test_db_session.query(models.Post).first()
        assert len(post.content) == 5000
        assert post.content == long_content
    
    def test_create_multiple_posts(self, test_client: TestClient, test_db_session):
        """Test creating multiple posts in sequence"""
        posts_data = [
            ("First Post", "First content", "First Author"),
            ("Second Post", "Second content", "Second Author"),
            ("Third Post", "Third content", "Third Author")
        ]
        
        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
            }
        }
        """
        
        for title, content, author in posts_data:
            variables = {
                "input": {
                    "title": title,
                    "content": content,
                    "author": author
                }
            }
            
            response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
            assert response.status_code == 200
            assert response.json()["data"]["createNewPost"]["ok"] is True
        
        # Verify all posts were created
        posts = test_db_session.query(models.Post).all()
        assert len(posts) == 3
        
        titles = [post.title for post in posts]
        contents = [post.content for post in posts]
        authors = [post.author for post in posts]
        assert "First Post" in titles
        assert "Second Post" in titles
        assert "Third Post" in titles
        assert "First content" in contents
        assert "Second content" in contents
        assert "Third content" in contents
        assert "First Author" in authors
        assert "Second Author" in authors
        assert "Third Author" in authors

    def test_create_new_post_missing_title(self, test_client: TestClient):
        """Test createNewPost mutation without required title parameter"""
        mutation = """
        mutation CreatePostMissingTitle($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
            }
        }
        """
        
        variables = {
            "input": {
                "content": "Content without title",
                "author": "Test Author"
                # title is missing - should cause GraphQL validation error
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
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
        mutation CreatePostMissingContent($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
            }
        }
        """
        
        variables = {
            "input": {
                "title": "Title without content",
                "author": "Test Author"
                # content is missing - should cause GraphQL validation error
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        # Should mention missing required argument
        error_message = str(data["errors"][0])
        assert "content" in error_message.lower()

    def test_create_new_post_missing_author(self, test_client: TestClient):
        """Test createNewPost mutation without required author parameter"""
        mutation = """
        mutation CreatePostMissingAuthor($input: CreatePostInput!) {
            createNewPost(input: $input) {
                ok
            }
        }
        """
        
        variables = {
            "input": {
                "title": "Title without author",
                "content": "Content without author"
                # author is missing - should cause GraphQL validation error
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        # Should mention missing required argument
        error_message = str(data["errors"][0])
        assert "author" in error_message.lower()

    def test_invalid_mutation_syntax(self, test_client: TestClient):
        """Test invalid GraphQL mutation syntax"""
        invalid_mutation = """
        mutation {
            createNewPost(title: "Test" content: "Missing comma") {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": invalid_mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0

    def test_nonexistent_mutation(self, test_client: TestClient):
        """Test calling non-existent mutation"""
        nonexistent_mutation = """
        mutation {
            nonExistentMutation(id: 1) {
                ok
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": nonexistent_mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0


class TestUpdatePostMutation:
    """Test updatePost GraphQL mutation with Input Objects"""
    
    def test_update_post_success(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test successful post update"""
        # Create a sample post
        post = create_sample_post(title="Original Title", content="Original content")
        
        mutation = """
        mutation UpdatePost($id: Int!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                ok
                error
                post {
                    id
                    title
                    content
                    author
                }
            }
        }
        """
        
        variables = {
            "id": post.id,
            "input": {
                "title": "Updated Title",
                "content": "Updated content"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["updatePost"]["ok"] is True
        assert data["data"]["updatePost"]["error"] is None
        assert data["data"]["updatePost"]["post"]["title"] == "Updated Title"
        assert data["data"]["updatePost"]["post"]["content"] == "Updated content"
        assert data["data"]["updatePost"]["post"]["author"] == "Sample Author"  # Unchanged
    
    def test_update_post_partial_fields(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test updating only specific fields using exclude_unset"""
        # Create a sample post
        post = create_sample_post(title="Keep Title", content="Keep Content", author="Change Author")
        
        mutation = """
        mutation UpdatePostPartial($id: Int!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                ok
                post {
                    title
                    content
                    author
                }
            }
        }
        """
        
        # Only update author field
        variables = {
            "id": post.id,
            "input": {
                "author": "New Author"
                # title and content not provided - should remain unchanged
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["updatePost"]["ok"] is True
        post_data = data["data"]["updatePost"]["post"]
        assert post_data["title"] == "Keep Title"  # Unchanged
        assert post_data["content"] == "Keep Content"  # Unchanged  
        assert post_data["author"] == "New Author"  # Updated
    
    def test_update_post_nonexistent_id(self, test_client: TestClient):
        """Test updating post with non-existent ID"""
        mutation = """
        mutation UpdatePostNonExistent($id: Int!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                ok
                error
            }
        }
        """
        
        variables = {
            "id": 99999,
            "input": {
                "title": "Updated Title"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updatePost"]["ok"] is False
        assert "not found" in data["data"]["updatePost"]["error"]
    
    def test_update_post_validation_error(self, test_client: TestClient, create_sample_post):
        """Test updating post with validation errors"""
        post = create_sample_post()
        
        mutation = """
        mutation UpdatePostValidation($id: Int!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                ok
                error
            }
        }
        """
        
        variables = {
            "id": post.id,
            "input": {
                "title": "   "  # Whitespace-only title should fail
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["updatePost"]["ok"] is False
        assert "title" in data["data"]["updatePost"]["error"].lower()

    def test_update_post_with_author(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test updating post with author field"""
        # Create a sample post
        post = create_sample_post(title="Original Title", content="Original content", author="Original Author")
        
        mutation = """
        mutation UpdatePostAuthor($id: Int!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                ok
                post {
                    id
                    title
                    content
                    author
                }
            }
        }
        """
        
        variables = {
            "id": post.id,
            "input": {
                "author": "New Author Name"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"]["updatePost"]["ok"] is True
        post_data = data["data"]["updatePost"]["post"]
        assert post_data["title"] == "Original Title"  # Unchanged
        assert post_data["content"] == "Original content"  # Unchanged
        assert post_data["author"] == "New Author Name"  # Updated

    def test_update_post_empty_update(self, test_client: TestClient, create_sample_post):
        """Test updating post with empty input object"""
        post = create_sample_post()
        
        mutation = """
        mutation UpdatePostEmpty($id: Int!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                ok
                post {
                    title
                    content
                    author
                }
            }
        }
        """
        
        variables = {
            "id": post.id,
            "input": {}
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should succeed - empty input means no changes (exclude_unset)
        assert data["data"]["updatePost"]["ok"] is True
        post_data = data["data"]["updatePost"]["post"]
        assert post_data["title"] == "Sample Post"  # Unchanged
        assert post_data["content"] == "Sample content"  # Unchanged
        assert post_data["author"] == "Sample Author"  # Unchanged

    def test_update_post_missing_required_id(self, test_client: TestClient):
        """Test updatePost mutation without required id parameter"""
        mutation = """
        mutation UpdatePostNoId($input: UpdatePostInput!) {
            updatePost(input: $input)
        }
        """
        
        variables = {
            "input": {
                "title": "New Title"
            }
        }
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0


class TestDeletePostMutation:
    """Test deletePost GraphQL mutation"""
    
    def test_delete_post_success(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test successful post deletion"""
        # Create a post to delete
        post = create_sample_post()
        post_id = post.id
        
        mutation = """
        mutation DeletePost($id: Int!) {
            deletePost(id: $id) {
                ok
                error
            }
        }
        """
        
        variables = {"id": post_id}
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deletePost"]["ok"] is True
        assert data["data"]["deletePost"]["error"] is None
        
        # Verify post was deleted from database
        deleted_post = test_db_session.query(models.Post).filter(models.Post.id == post_id).first()
        assert deleted_post is None
    
    def test_delete_post_nonexistent_id(self, test_client: TestClient):
        """Test deleting post with non-existent ID"""
        mutation = """
        mutation DeletePostNonExistent($id: Int!) {
            deletePost(id: $id) {
                ok
                error
            }
        }
        """
        
        variables = {"id": 99999}
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deletePost"]["ok"] is False
        assert "not found" in data["data"]["deletePost"]["error"]

    def test_delete_post_missing_required_id(self, test_client: TestClient):
        """Test deletePost mutation without required id parameter"""
        mutation = """
        mutation DeletePostNoId {
            deletePost
        }
        """
        
        response = test_client.post("/graphql/", json={"query": mutation})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0

    def test_delete_post_selective_deletion(self, test_client: TestClient, test_db_session, create_sample_post):
        """Test deleting specific post among multiple posts"""
        # Create multiple posts
        post1 = create_sample_post(title="Keep Me 1", content="Content 1", author="Author 1")
        post2 = create_sample_post(title="Delete Me", content="Content 2", author="Author 2")  
        post3 = create_sample_post(title="Keep Me 3", content="Content 3", author="Author 3")
        
        # Delete the middle post
        mutation = """
        mutation DeleteSpecificPost($id: Int!) {
            deletePost(id: $id) {
                ok
                error
            }
        }
        """
        
        variables = {"id": post2.id}
        
        response = test_client.post("/graphql/", json={"query": mutation, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["deletePost"]["ok"] is True
        assert data["data"]["deletePost"]["error"] is None
        
        # Verify only the target post was deleted
        remaining_posts = test_db_session.query(models.Post).all()
        assert len(remaining_posts) == 2
        
        remaining_titles = [post.title for post in remaining_posts]
        assert "Keep Me 1" in remaining_titles
        assert "Keep Me 3" in remaining_titles
        assert "Delete Me" not in remaining_titles