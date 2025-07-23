from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db_conf import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(String)
    time_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
