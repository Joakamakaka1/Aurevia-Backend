from sqlalchemy.orm import Session
from typing import cast
from app.db.models.user import User
from app.auth.security import verify_password, hash_password
from app.core.exceptions import AppError

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create(db: Session, *, email: str, username: str, password: str, role: str = "user") -> User:
    # Validar duplicados primero
    if get_by_email(db, email):
        raise AppError(409, "EMAIL_DUPLICATED", "El email ya está registrado")
    
    if get_by_username(db, username):
        raise AppError(409, "USERNAME_DUPLICATED", "El nombre de usuario ya está registrado")
    
    # Validar formato/longitud (la longitud también se valida en el schema, pero mantenemos por si acaso)
    if len(username) < 3:
        raise AppError(400, "USERNAME_TOO_SHORT", "El nombre de usuario debe tener al menos 3 caracteres")
    
    if len(username) > 50:
        raise AppError(400, "USERNAME_TOO_LONG", "El nombre de usuario no puede tener más de 50 caracteres")
    
    # HASHEAR LA CONTRASEÑA ANTES DE GUARDARLA
    hashed_pwd = hash_password(password)
    
    # Crear usuario después de todas las validaciones (incluyendo role)
    user = User(email=email, username=username, hashed_password=hashed_pwd, role=role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate(db: Session, *, email: str, password: str) -> User:
    user = get_by_email(db, email)
    if not user:
        raise AppError(404, "EMAIL_NOT_FOUND", "El email no existe")

    # VERIFICAR CONTRASEÑA HASHEADA
    if not verify_password(password, cast(str, user.hashed_password)):
        raise AppError(400, "INVALID_PASSWORD", "La contraseña no es correcta")
    return user

def update_user_by_id(db: Session, user_id: int, user_data: dict) -> User:
    # Reutilizar get_user_by_id en lugar de duplicar la query
    user = get_user_by_id(db, user_id)
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    
    # Validar email duplicado (excluyendo el mismo usuario)
    if 'email' in user_data and user_data['email'] is not None:
        existing_user = get_by_email(db, user_data['email'])
        if existing_user and existing_user.id != user_id:
            raise AppError(409, "EMAIL_DUPLICATED", "El email ya está registrado por otro usuario")
    
    # Validar username duplicado (excluyendo el mismo usuario)
    if 'username' in user_data and user_data['username'] is not None:
        existing_user = get_by_username(db, user_data['username'])
        if existing_user and existing_user.id != user_id:
            raise AppError(409, "USERNAME_DUPLICATED", "El nombre de usuario ya está registrado por otro usuario")
        
        # Validar longitud de username
        username = user_data['username']
        if len(username) < 3:
            raise AppError(400, "USERNAME_TOO_SHORT", "El nombre de usuario debe tener al menos 3 caracteres")
        if len(username) > 50:
            raise AppError(400, "USERNAME_TOO_LONG", "El nombre de usuario no puede tener más de 50 caracteres")
    
    # SI SE ESTÁ ACTUALIZANDO LA CONTRASEÑA, HASHEARLA PRIMERO
    if 'password' in user_data and user_data['password'] is not None:
        # Hashear y guardar con el nombre correcto del campo en la BD
        hashed = hash_password(user_data['password'])
        user_data['hashed_password'] = hashed
        # Eliminar 'password' del dict para no intentar asignar un campo que no existe en el modelo
        del user_data['password']

    # Actualizar solo los campos que no son None
    for key, value in user_data.items():
        if value is not None:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_id(db: Session, user_id: int) -> None:
    # Reutilizar get_user_by_id en lugar de duplicar la query
    user = get_user_by_id(db, user_id)
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")

    db.delete(user)
    db.commit()