from sqlalchemy.orm import Session
from . import models, schemas

def get_user_by_username(db: Session, username: str):
    """
    Obtiene un usuario por su nombre de usuario.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Crea un nuevo usuario en la base de datos.
    """
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