from sqlalchemy import DateTime, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db_conf import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String(10000), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    time_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_empty"),
        CheckConstraint("length(trim(content)) > 0", name="content_not_empty"),
        CheckConstraint("length(trim(author)) > 0", name="author_not_empty"),
    )
