import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from db_conf import db_session
from models import Post


class PostCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, max_length=10000, description="Post content")
    author: str = Field(..., min_length=1, max_length=100, description="Post author")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('author')
    @classmethod
    def validate_author(cls, v):
        if not v.strip():
            raise ValueError('Author cannot be empty or whitespace only')
        return v.strip()


class PostUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Post title")
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="Post content")
    author: Optional[str] = Field(None, min_length=1, max_length=100, description="Post author")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip() if v else v
    
    @field_validator('author')
    @classmethod
    def validate_author(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Author cannot be empty or whitespace only')
        return v.strip() if v else v


# GraphQL Input Objects
class CreatePostInput(graphene.InputObjectType):
    """Input type for creating a new post"""
    title = graphene.String(required=True, description="Post title (1-200 characters)")
    content = graphene.String(required=True, description="Post content (1-10000 characters)")
    author = graphene.String(required=True, description="Post author (1-100 characters)")


class UpdatePostInput(graphene.InputObjectType):
    """Input type for updating an existing post"""
    title = graphene.String(description="Post title (1-200 characters)")
    content = graphene.String(description="Post content (1-10000 characters)")
    author = graphene.String(description="Post author (1-100 characters)")


class PostModel(SQLAlchemyObjectType):
    class Meta:
        model = Post
        load_instance = True
        sqla_session = db_session


# Simple Pagination Types
class PostPagination(graphene.ObjectType):
    """Pagination metadata"""
    current_page = graphene.Int(description="Current page number")
    total_pages = graphene.Int(description="Total number of pages")
    total_count = graphene.Int(description="Total number of posts")
    has_next_page = graphene.Boolean(description="Whether there is a next page")
    has_previous_page = graphene.Boolean(description="Whether there is a previous page")


class PostsResponse(graphene.ObjectType):
    """Response type for paginated posts"""
    posts = graphene.List(PostModel, description="List of posts")
    pagination = graphene.Field(PostPagination, description="Pagination metadata")
