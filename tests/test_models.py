"""
Test SQLAlchemy models
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

import models
from tests.factories import create_post_factory


class TestPostModel:
    """Test Post model functionality"""
    
    def test_create_post_basic(self, test_db_session):
        """Test basic post creation"""
        post = models.Post(
            title="Test Post",
            content="Test content for the post",
            author="Test Author"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.content == "Test content for the post"
        assert post.author == "Test Author"  # required field
        assert isinstance(post.time_created, datetime)
    
    def test_create_post_with_author(self, test_db_session):
        """Test post creation with author"""
        post = models.Post(
            title="Authored Post",
            content="Content by author",
            author="John Doe"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        assert post.author == "John Doe"
        assert post.title == "Authored Post"
        assert post.content == "Content by author"
    
    def test_post_time_created_auto_generated(self, test_db_session):
        """Test that time_created is automatically set"""
        post = models.Post(
            title="Time Test Post",
            content="Testing automatic timestamp",
            author="Time Test Author"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        assert post.time_created is not None
        assert isinstance(post.time_created, datetime)
    
    def test_post_string_fields_validation_constraints(self, test_db_session):
        """Test that database constraints prevent empty title and content"""
        import pytest
        from sqlalchemy.exc import IntegrityError
        
        # Test empty title constraint
        post = models.Post(
            title="",
            content="Valid content",
            author="Test Author"
        )
        
        test_db_session.add(post)
        try:
            test_db_session.commit()
            pytest.fail("Expected IntegrityError for empty title constraint")
        except IntegrityError as e:
            assert "title_not_empty" in str(e)
        test_db_session.rollback()
        
        # Test empty content constraint  
        post = models.Post(
            title="Valid title",
            content="",
            author="Test Author"
        )
        
        test_db_session.add(post)
        try:
            test_db_session.commit()
            pytest.fail("Expected IntegrityError for empty content constraint")
        except IntegrityError as e:
            assert "content_not_empty" in str(e)
        test_db_session.rollback()
        
        # Test that author cannot be empty string due to constraint
        post = models.Post(
            title="Valid title",
            content="Valid content",
            author=""
        )
        
        test_db_session.add(post)
        try:
            test_db_session.commit()
            pytest.fail("Expected IntegrityError for empty author constraint")
        except IntegrityError as e:
            assert "author_not_empty" in str(e)
        test_db_session.rollback()
        
        # Test that author is required (NOT NULL constraint)
        post = models.Post(
            title="Valid title",
            content="Valid content"
            # author is missing completely
        )
        
        test_db_session.add(post)
        try:
            test_db_session.commit()
            pytest.fail("Expected IntegrityError for null author constraint")
        except IntegrityError as e:
            assert "not null" in str(e).lower() or "null value" in str(e).lower()
        test_db_session.rollback()
    
    def test_post_with_unicode_content(self, test_db_session):
        """Test post with unicode characters"""
        post = models.Post(
            title="Unicode Test 🚀",
            content="Content with émojis 😄 and special chars: àáâãäå",
            author="José María"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        assert "🚀" in post.title
        assert "😄" in post.content
        assert "émojis" in post.content
        assert post.author == "José María"
    
    def test_post_with_long_content(self, test_db_session):
        """Test post with very long content"""
        long_content = "A" * 10000  # 10k characters
        
        post = models.Post(
            title="Long Content Post",
            content=long_content,
            author="Long Content Author"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        assert len(post.content) == 10000
        assert post.content == long_content
    
    def test_post_query_by_id(self, test_db_session):
        """Test querying post by ID"""
        post = models.Post(
            title="Query Test",
            content="Testing query functionality",
            author="Query Test Author"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        # Query by ID
        found_post = test_db_session.query(models.Post).filter(
            models.Post.id == post.id
        ).first()
        
        assert found_post is not None
        assert found_post.id == post.id
        assert found_post.title == "Query Test"
    
    def test_post_query_by_title(self, test_db_session):
        """Test querying post by title"""
        post1 = models.Post(title="First Post", content="Content 1", author="First Author")
        post2 = models.Post(title="Second Post", content="Content 2", author="Second Author")
        
        test_db_session.add_all([post1, post2])
        test_db_session.commit()
        
        found_post = test_db_session.query(models.Post).filter(
            models.Post.title == "Second Post"
        ).first()
        
        assert found_post is not None
        assert found_post.title == "Second Post"
        assert found_post.content == "Content 2"
    
    def test_post_query_all(self, test_db_session):
        """Test querying all posts"""
        posts = [
            models.Post(title=f"Post {i}", content=f"Content {i}", author=f"Author {i}")
            for i in range(5)
        ]
        
        test_db_session.add_all(posts)
        test_db_session.commit()
        
        all_posts = test_db_session.query(models.Post).all()
        
        assert len(all_posts) == 5
        titles = [post.title for post in all_posts]
        for i in range(5):
            assert f"Post {i}" in titles
    
    def test_post_update(self, test_db_session):
        """Test updating post fields"""
        post = models.Post(
            title="Original Title",
            content="Original content",
            author="Original Author"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        test_db_session.refresh(post)
        
        # Update fields
        post.title = "Updated Title"
        post.content = "Updated content"
        post.author = "New Author"
        
        test_db_session.commit()
        test_db_session.refresh(post)
        
        assert post.title == "Updated Title"
        assert post.content == "Updated content"
        assert post.author == "New Author"
    
    def test_post_delete(self, test_db_session):
        """Test deleting a post"""
        post = models.Post(
            title="To be deleted",
            content="This post will be deleted",
            author="To be deleted author"
        )
        
        test_db_session.add(post)
        test_db_session.commit()
        post_id = post.id
        
        # Delete the post
        test_db_session.delete(post)
        test_db_session.commit()
        
        # Verify deletion
        found_post = test_db_session.query(models.Post).filter(
            models.Post.id == post_id
        ).first()
        
        assert found_post is None


class TestPostFactory:
    """Test PostFactory functionality"""
    
    def test_post_factory_creates_valid_post(self, test_db_session):
        """Test that PostFactory creates valid post instances"""
        PostFactory = create_post_factory(test_db_session)
        post = PostFactory()
        
        assert post.id is not None
        assert isinstance(post.title, str)
        assert isinstance(post.content, str)
        assert isinstance(post.author, str)
        assert post.time_created is not None
        
        # Verify it's actually in the database
        db_post = test_db_session.query(models.Post).filter(
            models.Post.id == post.id
        ).first()
        assert db_post is not None
    
    def test_post_factory_with_custom_values(self, test_db_session):
        """Test PostFactory with custom values"""
        PostFactory = create_post_factory(test_db_session)
        post = PostFactory(
            title="Custom Title",
            content="Custom content for testing"
        )
        
        assert post.title == "Custom Title"
        assert post.content == "Custom content for testing"
        assert isinstance(post.author, str)  # Should be generated
    
    def test_post_factory_batch_creation(self, test_db_session):
        """Test creating multiple posts with factory"""
        PostFactory = create_post_factory(test_db_session)
        posts = PostFactory.create_batch(5)
        
        assert len(posts) == 5
        
        # Verify all are in database
        db_posts = test_db_session.query(models.Post).all()
        assert len(db_posts) == 5
        
        # Verify they have different titles (high probability)
        titles = [post.title for post in posts]
        assert len(set(titles)) > 1  # Should have some variety