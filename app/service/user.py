from sqlalchemy.orm import Session
from typing import cast
from app.db.models.user import User
from app.auth.security import verify_password
from app.core.exceptions import AppError

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create(db: Session, *, email: str, username: str, password: str) -> User:
    if get_by_email(db, email):
        raise AppError(409, "EMAIL_DUPLICATED", "El email ya está registrado")
    user = User(email=email, username=username, hashed_password=password)

    if len(username) < 3:
        raise AppError(400, "USERNAME_TOO_SHORT", "El nombre de usuario debe tener al menos 3 caracteres")

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
def authenticate(db: Session, *, email: str, password: str) -> User:
    user = get_by_email(db, email)
    if not user:
        raise AppError(404, "EMAIL_NOT_FOUND", "El email no existe")

    if not verify_password(password, cast(str, user.hashed_password)):
        raise AppError(400, "INVALID_PASSWORD", "La contraseña no es correcta")
    return user

def update_user_by_id(db: Session, user_id: int, user_data) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    
    if 'email' in user_data:
        existing_user = get_by_email(db, user_data['email'])
        if existing_user:
            raise AppError(409, "EMAIL_DUPLICATED", "El email ya está registrado por otro usuario")

    for key, value in user_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_id(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")

    db.delete(user)
    db.commit()