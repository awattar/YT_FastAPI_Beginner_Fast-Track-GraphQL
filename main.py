import graphene
from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp

import models
from db_conf import db_session
from schemas import PostModel, PostSchema
from graphiql_handler import make_custom_graphiql_handler

db = db_session.session_factory()

app = FastAPI()


class Query(graphene.ObjectType):

    all_posts = graphene.List(PostModel)
    post_by_id = graphene.Field(PostModel, post_id=graphene.Int(required=True))

    def resolve_all_posts(self, info):
        return db.query(models.Post).all()

    def resolve_post_by_id(self, info, post_id):
        return db.query(models.Post).filter(models.Post.id == post_id).first()


class CreateNewPost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, title, content):
        post = PostSchema(title=title, content=content)
        db_post = models.Post(title=post.title, content=post.content)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        ok = True
        return CreateNewPost(ok=ok)


class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()
        author = graphene.String()

    ok = graphene.Boolean()
    post = graphene.Field(PostModel)
    error = graphene.String()

    @staticmethod
    def mutate(root, info, id, title=None, content=None, author=None):
        # Find the post to update
        db_post = db.query(models.Post).filter(models.Post.id == id).first()
        
        if not db_post:
            return UpdatePost(ok=False, error=f"Post with id {id} not found")
        
        # Update only provided fields
        if title is not None:
            db_post.title = title
        if content is not None:
            db_post.content = content
        if author is not None:
            db_post.author = author
        
        try:
            db.commit()
            db.refresh(db_post)
            return UpdatePost(ok=True, post=db_post)
        except Exception as e:
            db.rollback()
            return UpdatePost(ok=False, error=f"Failed to update post: {str(e)}")


class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    error = graphene.String()

    @staticmethod
    def mutate(root, info, id):
        # Find the post to delete
        db_post = db.query(models.Post).filter(models.Post.id == id).first()
        
        if not db_post:
            return DeletePost(ok=False, error=f"Post with id {id} not found")
        
        try:
            db.delete(db_post)
            db.commit()
            return DeletePost(ok=True)
        except Exception as e:
            db.rollback()
            return DeletePost(ok=False, error=f"Failed to delete post: {str(e)}")


class PostMutations(graphene.ObjectType):
    create_new_post = CreateNewPost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()


app.mount("/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=PostMutations), on_get=make_custom_graphiql_handler()))
