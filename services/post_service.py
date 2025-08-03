"""Post service for business logic operations"""
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import math

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
    
    # Simple Pagination Method
    def get_posts_paginated(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[models.Post], int, int, int, bool, bool]:
        """
        Get paginated posts using simple offset/limit pagination
        
        Args:
            page: Page number (1-based)
            limit: Number of posts per page
            
        Returns:
            Tuple of (posts, total_count, total_pages, current_page, has_next_page, has_previous_page)
        """
        # Validate arguments
        if page < 1:
            raise ValueError("page must be >= 1")
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if limit > 100:
            raise ValueError("limit cannot exceed 100")
        
        # Get total count
        total_count = self.db.query(func.count(models.Post.id)).scalar()
        
        # Calculate pagination metadata
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
        has_next_page = page < total_pages
        has_previous_page = page > 1
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get posts for current page
        posts = (
            self.db.query(models.Post)
            .order_by(desc(models.Post.id))  # Newest first
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return posts, total_count, total_pages, page, has_next_page, has_previous_page