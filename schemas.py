from graphene_sqlalchemy import SQLAlchemyObjectType
from pydantic import BaseModel

from db_conf import db_session
from models import Post


class PostSchema(BaseModel):
    title: str
    content: str


class PostModel(SQLAlchemyObjectType):
    class Meta:
        model = Post
        load_instance = True
        sqla_session = db_session
