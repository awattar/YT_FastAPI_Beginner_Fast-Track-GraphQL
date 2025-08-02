"""
Test PostService business logic layer
"""
import pytest
from pydantic import ValidationError

import models
from services.post_service import PostService
from schemas import PostCreateSchema, PostUpdateSchema


class TestPostService:
    """Test PostService business logic"""

    def test_create_post_success(self, test_db_session):
        """Test successful post creation through service"""
        service = PostService(test_db_session)
        post_data = PostCreateSchema(
            title="Service Test Post",
            content="Content created through service",
            author="Service Author"
        )
        
        created_post = service.create_post(post_data)
        
        assert created_post.id is not None
        assert created_post.title == "Service Test Post"
        assert created_post.content == "Content created through service"
        assert created_post.author == "Service Author"
        assert created_post.time_created is not None
        
        # Verify in database
        db_post = test_db_session.query(models.Post).filter(models.Post.id == created_post.id).first()
        assert db_post is not None
        assert db_post.title == "Service Test Post"

    def test_get_post_by_id_success(self, test_db_session, create_sample_post):
        """Test retrieving post by ID through service"""
        service = PostService(test_db_session)
        
        # Create a test post
        sample_post = create_sample_post(title="Find Me", content="I'm here", author="Finder")
        
        # Retrieve through service
        found_post = service.get_post_by_id(sample_post.id)
        
        assert found_post is not None
        assert found_post.id == sample_post.id
        assert found_post.title == "Find Me"
        assert found_post.content == "I'm here"
        assert found_post.author == "Finder"

    def test_get_post_by_id_not_found(self, test_db_session):
        """Test retrieving non-existent post returns None"""
        service = PostService(test_db_session)
        
        found_post = service.get_post_by_id(99999)
        
        assert found_post is None

    def test_get_all_posts_empty(self, test_db_session):
        """Test getting all posts when database is empty"""
        service = PostService(test_db_session)
        
        posts = service.get_all_posts()
        
        assert posts == []

    def test_get_all_posts_multiple(self, test_db_session, create_sample_post):
        """Test getting all posts with multiple posts in database"""
        service = PostService(test_db_session)
        
        # Create multiple posts
        post1 = create_sample_post(title="First Post", content="First", author="Author1")
        post2 = create_sample_post(title="Second Post", content="Second", author="Author2")
        post3 = create_sample_post(title="Third Post", content="Third", author="Author3")
        
        posts = service.get_all_posts()
        
        assert len(posts) == 3
        post_titles = [post.title for post in posts]
        assert "First Post" in post_titles
        assert "Second Post" in post_titles
        assert "Third Post" in post_titles

    def test_update_post_success_single_field(self, test_db_session, create_sample_post):
        """Test updating single field using exclude_unset functionality"""
        service = PostService(test_db_session)
        
        # Create initial post
        original_post = create_sample_post(
            title="Original Title",
            content="Original Content", 
            author="Original Author"
        )
        
        # Update only the title
        update_data = {"title": "Updated Title"}
        updated_post = service.update_post(original_post.id, update_data)
        
        assert updated_post.title == "Updated Title"
        assert updated_post.content == "Original Content"  # Unchanged
        assert updated_post.author == "Original Author"  # Unchanged
        
        # Verify in database
        test_db_session.refresh(original_post)
        assert original_post.title == "Updated Title"
        assert original_post.content == "Original Content"
        assert original_post.author == "Original Author"

    def test_update_post_success_multiple_fields(self, test_db_session, create_sample_post):
        """Test updating multiple fields"""
        service = PostService(test_db_session)
        
        # Create initial post
        original_post = create_sample_post(
            title="Old Title",
            content="Old Content",
            author="Old Author"
        )
        
        # Update title and content, leave author unchanged
        update_data = {
            "title": "New Title",
            "content": "New Content"
        }
        updated_post = service.update_post(original_post.id, update_data)
        
        assert updated_post.title == "New Title"
        assert updated_post.content == "New Content"
        assert updated_post.author == "Old Author"  # Unchanged due to exclude_unset

    def test_update_post_not_found(self, test_db_session):
        """Test updating non-existent post raises ValueError"""
        service = PostService(test_db_session)
        
        with pytest.raises(ValueError) as excinfo:
            service.update_post(99999, {"title": "New Title"})
        
        assert "Post with id 99999 not found" in str(excinfo.value)

    def test_update_post_validation_error(self, test_db_session, create_sample_post):
        """Test updating post with invalid data raises ValidationError"""
        service = PostService(test_db_session)
        
        # Create initial post
        original_post = create_sample_post(title="Valid", content="Valid", author="Valid")
        
        # Try to update with invalid data
        with pytest.raises(ValidationError):
            service.update_post(original_post.id, {"title": ""})  # Empty title

    def test_update_post_exclude_unset_demonstration(self, test_db_session, create_sample_post):
        """Test that exclude_unset=True only updates provided fields"""
        service = PostService(test_db_session)
        
        # Create initial post
        original_post = create_sample_post(
            title="Keep Title",
            content="Keep Content",
            author="Change Me"
        )
        
        # Update only author field - title and content should remain unchanged
        update_data = {"author": "New Author"}
        updated_post = service.update_post(original_post.id, update_data)
        
        # Verify only author changed
        assert updated_post.title == "Keep Title"  # Unchanged
        assert updated_post.content == "Keep Content"  # Unchanged
        assert updated_post.author == "New Author"  # Changed
        
        # Now update only content
        update_data = {"content": "New Content"}
        updated_post = service.update_post(original_post.id, update_data)
        
        # Verify only content changed
        assert updated_post.title == "Keep Title"  # Still unchanged
        assert updated_post.content == "New Content"  # Changed
        assert updated_post.author == "New Author"  # Still from previous update

    def test_delete_post_success(self, test_db_session, create_sample_post):
        """Test successful post deletion"""
        service = PostService(test_db_session)
        
        # Create post to delete
        post_to_delete = create_sample_post(title="Delete Me", content="Gone", author="Deleted")
        post_id = post_to_delete.id
        
        # Delete the post
        result = service.delete_post(post_id)
        
        assert result is True
        
        # Verify post is deleted
        deleted_post = test_db_session.query(models.Post).filter(models.Post.id == post_id).first()
        assert deleted_post is None

    def test_delete_post_not_found(self, test_db_session):
        """Test deleting non-existent post raises ValueError"""
        service = PostService(test_db_session)
        
        with pytest.raises(ValueError) as excinfo:
            service.delete_post(99999)
        
        assert "Post with id 99999 not found" in str(excinfo.value)

    def test_service_with_custom_database_session(self, test_db_session):
        """Test that service works with custom database session"""
        # Create service with specific session
        service = PostService(test_db_session)
        
        # Create post
        post_data = PostCreateSchema(
            title="Custom Session Test",
            content="Using custom session",
            author="Session Tester"
        )
        created_post = service.create_post(post_data)
        
        # Verify post exists in the specific session
        found_post = test_db_session.query(models.Post).filter(
            models.Post.id == created_post.id
        ).first()
        assert found_post is not None
        assert found_post.title == "Custom Session Test"

    def test_service_pydantic_validation_integration(self, test_db_session):
        """Test that service properly integrates with Pydantic validation"""
        service = PostService(test_db_session)
        
        # Test create with validation
        post_data = PostCreateSchema(
            title="  Trimmed Title  ",  # Should be trimmed
            content="  Trimmed Content  ",  # Should be trimmed
            author="  Trimmed Author  "  # Should be trimmed
        )
        created_post = service.create_post(post_data)
        
        # Verify trimming occurred
        assert created_post.title == "Trimmed Title"
        assert created_post.content == "Trimmed Content"
        assert created_post.author == "Trimmed Author"
        
        # Test update with validation
        update_data = {"title": "  New Trimmed Title  "}
        updated_post = service.update_post(created_post.id, update_data)
        
        assert updated_post.title == "New Trimmed Title"