"""
Test data factories using factory_boy
"""
import factory
from factory.alchemy import SQLAlchemyModelFactory

import models


class PostFactory(SQLAlchemyModelFactory):
    """Factory for creating Post instances in tests"""
    
    class Meta:
        model = models.Post
        sqlalchemy_session_persistence = "commit"
    
    title = factory.Faker("sentence", nb_words=4)
    content = factory.Faker("text", max_nb_chars=500)
    author = factory.Faker("name")


def create_post_factory(session):
    """Create PostFactory with specific session"""
    class SessionPostFactory(PostFactory):
        class Meta:
            model = models.Post
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"
    
    return SessionPostFactory