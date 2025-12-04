from sqlalchemy.orm import Session
from typing import cast
from app.db.models.user import User
from app.auth.security import verify_password, hash_password
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.user import UserRepository

def get_all_users(db: Session) -> list[User]:
    repo = UserRepository(db)
    return repo.get_all()

def get_by_email(db: Session, email: str) -> User | None:
    repo = UserRepository(db)
    return repo.get_by_email(email)

def get_by_username(db: Session, username: str) -> User | None:
    repo = UserRepository(db)
    return repo.get_by_username(username)

def get_user_by_id(db: Session, user_id: int) -> User | None:
    repo = UserRepository(db)
    return repo.get_by_id(user_id)

@transactional
def create(db: Session, *, email: str, username: str, password: str, role: str = "user") -> User:
    repo = UserRepository(db)
    
    # Validar duplicados
    if repo.get_by_email(email):
        raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "El email ya está registrado")
    
    if repo.get_by_username(username):
        raise AppError(409, ErrorCode.USERNAME_DUPLICATED, "El nombre de usuario ya está registrado")
    
    # Nota: Validaciones de longitud de username ya las hace Pydantic
    
    # HASHEAR LA CONTRASEÑA
    hashed_pwd = hash_password(password)
    
    # Crear usuario
    user = User(email=email, username=username, hashed_password=hashed_pwd, role=role)
    return repo.create(user)

def authenticate(db: Session, *, email: str, password: str) -> User:
    # Authenticate es de lectura, no necesita transacción de escritura, pero sí manejo de errores
    try:
        repo = UserRepository(db)
        user = repo.get_by_email(email)
        if not user:
            raise AppError(404, ErrorCode.EMAIL_NOT_FOUND, "El email no existe")

        # VERIFICAR CONTRASEÑA HASHEADA
        if not verify_password(password, cast(str, user.hashed_password)):
            raise AppError(400, ErrorCode.INVALID_PASSWORD, "La contraseña no es correcta")
        return user
    except AppError:
        raise
    except Exception as e:
        raise AppError(500, ErrorCode.INTERNAL_SERVER_ERROR, str(e))

@transactional
def update_user_by_id(db: Session, user_id: int, user_data: dict) -> User:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")
    
    # Validar email duplicado (excluyendo el mismo usuario)
    if 'email' in user_data and user_data['email'] is not None:
        existing_user = repo.get_by_email(user_data['email'])
        if existing_user and existing_user.id != user_id:
            raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "El email ya está registrado por otro usuario")
    
    # Validar username duplicado (excluyendo el mismo usuario)
    if 'username' in user_data and user_data['username'] is not None:
        existing_user = repo.get_by_username(user_data['username'])
        if existing_user and existing_user.id != user_id:
            raise AppError(409, ErrorCode.USERNAME_DUPLICATED, "El nombre de usuario ya está registrado por otro usuario")
    
    # SI SE ESTÁ ACTUALIZANDO LA CONTRASEÑA, HASHEARLA PRIMERO
    if 'password' in user_data and user_data['password'] is not None:
        hashed = hash_password(user_data['password'])
        user_data['hashed_password'] = hashed
        del user_data['password']

    # Actualizar campos
    for key, value in user_data.items():
        if value is not None:
            setattr(user, key, value)
    
    # El commit lo hace el decorador
    return user

@transactional
def delete_user_by_id(db: Session, user_id: int) -> None:
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")

    repo.delete(user)