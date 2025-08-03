import graphene
from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp
from pydantic import ValidationError
from contextvars import ContextVar
from typing import Optional
from graphql import GraphQLError

import models
from db_conf import db_session
from schemas import PostModel, PostCreateSchema, PostUpdateSchema, CreatePostInput, UpdatePostInput, PostsResponse, PostPagination
from services.post_service import PostService
from graphiql_handler import make_custom_graphiql_handler

# Default database session
default_db = db_session.session_factory()

# Context variable for test database sessions
test_db_context: ContextVar[Optional[object]] = ContextVar('test_db_context', default=None)

def get_db_session():
    """Get database session - uses test context if available, otherwise default"""
    test_db = test_db_context.get()
    return test_db if test_db is not None else default_db

app = FastAPI()


def format_validation_errors(validation_error: ValidationError) -> str:
    """Format Pydantic validation errors into readable error messages"""
    error_messages = []
    for err in validation_error.errors():
        loc = " → ".join(str(i) for i in err['loc'])
        msg = f"{loc}: {err['msg']}"
        error_messages.append(msg)
    return ", ".join(error_messages)


class Query(graphene.ObjectType):

    # Paginated posts query
    posts = graphene.Field(
        PostsResponse,
        page=graphene.Int(default_value=1, description="Page number (starts from 1)"),
        limit=graphene.Int(default_value=10, description="Number of posts per page (max 100)")
    )
    
    # Legacy query for backward compatibility
    all_posts = graphene.List(PostModel)
    post_by_id = graphene.Field(PostModel, post_id=graphene.Int(required=True))

    def resolve_posts(self, info, page=1, limit=10):
        """Resolve paginated posts using simple offset/limit pagination"""
        service = PostService(get_db_session())
        
        try:
            posts, total_count, total_pages, current_page, has_next_page, has_previous_page = service.get_posts_paginated(
                page=page, limit=limit
            )
            
            # Create pagination metadata
            pagination = PostPagination(
                current_page=current_page,
                total_pages=total_pages,
                total_count=total_count,
                has_next_page=has_next_page,
                has_previous_page=has_previous_page
            )
            
            # Return simple response
            return PostsResponse(posts=posts, pagination=pagination)
            
        except ValueError as e:
            # Handle pagination errors gracefully
            raise GraphQLError(str(e))

    def resolve_all_posts(self, info):
        """Legacy resolver - deprecated in favor of paginated 'posts' query"""
        service = PostService(get_db_session())
        return service.get_all_posts()

    def resolve_post_by_id(self, info, post_id):
        service = PostService(get_db_session())
        return service.get_post_by_id(post_id)


class CreateNewPost(graphene.Mutation):
    """Create a new post using Input Object"""
    class Arguments:
        input = CreatePostInput(required=True)

    ok = graphene.Boolean()
    post = graphene.Field(PostModel)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            service = PostService(get_db_session())
            post_data = PostCreateSchema(**input)
            db_post = service.create_post(post_data)
            return CreateNewPost(ok=True, post=db_post)
        except ValidationError as e:
            return CreateNewPost(ok=False, error=format_validation_errors(e))
        except Exception as e:
            get_db_session().rollback()
            return CreateNewPost(ok=False, error=f"Failed to create post: {str(e)}")


class UpdatePost(graphene.Mutation):
    """Update a post using Input Object with Pydantic exclude_unset"""
    class Arguments:
        id = graphene.Int(required=True)
        input = UpdatePostInput(required=True)

    ok = graphene.Boolean()
    post = graphene.Field(PostModel)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, id, input):
        try:
            service = PostService(get_db_session())
            db_post = service.update_post(id, input)
            return UpdatePost(ok=True, post=db_post)
        except ValidationError as e:
            return UpdatePost(ok=False, error=format_validation_errors(e))
        except ValueError as e:
            return UpdatePost(ok=False, error=str(e))
        except Exception as e:
            get_db_session().rollback()
            return UpdatePost(ok=False, error=f"Failed to update post: {str(e)}")


class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    error = graphene.String()

    @staticmethod
    def mutate(root, info, id):
        try:
            service = PostService(get_db_session())
            service.delete_post(id)
            return DeletePost(ok=True)
        except ValueError as e:
            return DeletePost(ok=False, error=str(e))
        except Exception as e:
            get_db_session().rollback()
            return DeletePost(ok=False, error=f"Failed to delete post: {str(e)}")


class PostMutations(graphene.ObjectType):
    create_new_post = CreateNewPost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()


app.mount("/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=PostMutations), on_get=make_custom_graphiql_handler()))
