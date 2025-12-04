from sqlalchemy.orm import Session
from typing import cast, List, Optional
from app.db.models.user import User
from app.auth.security import verify_password, hash_password
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.user import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def get_all(self) -> List[User]:
        return self.repo.get_all()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.repo.get_by_email(email)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.repo.get_by_username(username)

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.repo.get_by_id(user_id)

    @transactional
    def create(self, *, email: str, username: str, password: str, role: str = "user") -> User:
        # Validar duplicados
        if self.repo.get_by_email(email):
            raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "El email ya está registrado")
        
        if self.repo.get_by_username(username):
            raise AppError(409, ErrorCode.USERNAME_DUPLICATED, "El nombre de usuario ya está registrado")
        
        # HASHEAR LA CONTRASEÑA
        hashed_pwd = hash_password(password)
        
        # Crear usuario
        user = User(email=email, username=username, hashed_password=hashed_pwd, role=role)
        return self.repo.create(user)

    def authenticate(self, *, email: str, password: str) -> User:
        try:
            user = self.repo.get_by_email(email)
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
    def update(self, user_id: int, user_data: dict) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")
        
        # Validar email duplicado
        if 'email' in user_data and user_data['email'] is not None:
            existing_user = self.repo.get_by_email(user_data['email'])
            if existing_user and existing_user.id != user_id:
                raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "El email ya está registrado por otro usuario")
        
        # Validar username duplicado
        if 'username' in user_data and user_data['username'] is not None:
            existing_user = self.repo.get_by_username(user_data['username'])
            if existing_user and existing_user.id != user_id:
                raise AppError(409, ErrorCode.USERNAME_DUPLICATED, "El nombre de usuario ya está registrado por otro usuario")
        
        # SI SE ESTÁ ACTUALIZANDO LA CONTRASEÑA, HASHEARLA PRIMERO
        if 'password' in user_data and user_data['password'] is not None:
            hashed = hash_password(user_data['password'])
            user_data['hashed_password'] = hashed
            del user_data['password']

        return self.repo.update(user_id, user_data)

    @transactional
    def delete(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")

        self.repo.delete(user)