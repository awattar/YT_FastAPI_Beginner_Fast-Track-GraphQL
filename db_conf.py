import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

load_dotenv(".env")

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://user:password@localhost/dbname")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class Base(DeclarativeBase):
    pass
