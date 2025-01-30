from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    profile_image = Column(String, default="default_profile_image.png")

    # Relaciones
    posts = relationship("Post", back_populates="user")  # Un usuario tiene muchos posts
    comments = relationship("Comment", back_populates="user")  # Un usuario tiene muchos comentarios
    likes = relationship("Like", back_populates="user")  # Un usuario tiene muchos likes
    followers = relationship("Follower", foreign_keys="Follower.followed_id", back_populates="followed_user")  # Seguidores
    following = relationship("Follower", foreign_keys="Follower.follower_id", back_populates="follower_user")  # Siguiendo
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")  # Mensajes enviados
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")  # Mensajes recibidos


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    user = relationship("User", back_populates="posts")  # Un post pertenece a un usuario
    comments = relationship("Comment", back_populates="post")  # Un post tiene muchos comentarios
    likes = relationship("Like", back_populates="post")  # Un post tiene muchos likes


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    user = relationship("User", back_populates="comments")  # Un comentario pertenece a un usuario
    post = relationship("Post", back_populates="comments")  # Un comentario pertenece a un post

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    user = relationship("User", back_populates="likes")  # Un like pertenece a un usuario
    post = relationship("Post", back_populates="likes")  # Un like pertenece a un post





class Follower(Base):
    __tablename__ = "followers"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relaciones
    follower_user = relationship("User", foreign_keys=[follower_id], back_populates="following")  # Usuario que sigue
    followed_user = relationship("User", foreign_keys=[followed_id], back_populates="followers")  # Usuario seguido

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_read = Column(Boolean, default=False)

    # Relaciones
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")  # Usuario que envía el mensaje
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")  # Usuario que recibe el mensaje


class test(Base):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
