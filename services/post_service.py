"""Post service for business logic operations"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

import models
from schemas import PostCreateSchema, PostUpdateSchema
from db_conf import db_session


class PostService:
    """Service class for Post-related business operations"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or db_session.session_factory()
    
    def create_post(self, post_data: PostCreateSchema) -> models.Post:
        """Create a new post with validated data"""
        db_post = models.Post(
            title=post_data.title,
            content=post_data.content,
            author=post_data.author
        )
        
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)
        return db_post
    
    def get_post_by_id(self, post_id: int) -> Optional[models.Post]:
        """Get a post by ID"""
        return self.db.query(models.Post).filter(models.Post.id == post_id).first()
    
    def get_all_posts(self) -> list[models.Post]:
        """Get all posts"""
        return self.db.query(models.Post).all()
    
    def update_post(self, post_id: int, update_data: Dict[str, Any]) -> models.Post:
        """Update a post with validated data"""
        db_post = self.get_post_by_id(post_id)
        
        if not db_post:
            raise ValueError(f"Post with id {post_id} not found")
        
        # Validate the update data
        validated_data = PostUpdateSchema(**update_data)
        
        # Use Pydantic's model_dump with exclude_unset=True for dynamic updates
        update_fields = validated_data.model_dump(exclude_unset=True)
        
        # Apply updates dynamically
        for key, value in update_fields.items():
            setattr(db_post, key, value)
        
        self.db.commit()
        self.db.refresh(db_post)
        return db_post
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post by ID"""
        db_post = self.get_post_by_id(post_id)
        
        if not db_post:
            raise ValueError(f"Post with id {post_id} not found")
        
        self.db.delete(db_post)
        self.db.commit()
        return True