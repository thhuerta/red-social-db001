from sqlalchemy.orm import Session
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password,
        profile_image=user.profile_image
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(
        content=post.content,
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Post).offset(skip).limit(limit).all()

def create_comment(db: Session, comment: schemas.CommentCreate, user_id: int):
    db_comment = models.Comment(
        content=comment.content,
        user_id=user_id,
        post_id=comment.post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def create_like(db: Session, like: schemas.LikeCreate, user_id: int):
    db_like = models.Like(
        user_id=user_id,
        post_id=like.post_id
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return db_like

def create_follower(db: Session, follower: schemas.FollowerCreate, user_id: int):
    db_follower = models.Follower(
        follower_id=user_id,
        followed_id=follower.followed_id
    )
    db.add(db_follower)
    db.commit()
    db.refresh(db_follower)
    return db_follower

def create_message(db: Session, message: schemas.MessageCreate, user_id: int):
    db_message = models.Message(
        content=message.content,
        sender_id=user_id,
        receiver_id=message.receiver_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_users_to_follow(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    # Obtener usuarios que no sigues
    return db.query(models.User).filter(models.User.id != user_id).offset(skip).limit(limit).all()