from sqlalchemy import Column, Integer, String, Boolean, text, DateTime, func, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(250), nullable=False)
    content = Column(String(500), nullable=False)
    published = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rating = Column(Integer, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner=relationship("User")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Votes(Base):
    __tablename__= "votes"
    user_id=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id=Column(Integer, ForeignKey("post.id", ondelete="CASCADE"), primary_key=True)



