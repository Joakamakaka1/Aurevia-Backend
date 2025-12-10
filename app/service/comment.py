from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.comment import CommentRepository
from app.repository.user import UserRepository
from app.repository.trip import TripRepository

class CommentService:
    '''
    Servicio que maneja la lógica de negocio de comentarios.
    
    Responsabilidades:
    - Validación de longitud del contenido (5-200 caracteres)
    - Validación de integridad referencial (user_id, trip_id)
    '''
    def __init__(self, db: Session):
        self.db = db
        self.repo = CommentRepository(db)
        self.user_repo = UserRepository(db)
        self.trip_repo = TripRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Comment]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.repo.get_by_id(comment_id)

    def get_by_trip_id(self, trip_id: int) -> List[Comment]:
        return self.repo.get_by_trip_id(trip_id)

    def get_by_user_id(self, user_id: int) -> List[Comment]:
        return self.repo.get_by_user_id(user_id)

    def validate_comment_length(self, content: str) -> None:
        """Valida longitud del contenido del comentario"""
        if len(content) < 5:
            raise AppError(400, ErrorCode.COMMENT_TOO_SHORT, "El comentario debe tener al menos 5 caracteres")
        if len(content) > 200:
            raise AppError(400, ErrorCode.COMMENT_TOO_LONG, "El comentario no puede tener más de 200 caracteres")

    @transactional
    def create(self, comment_in: CommentCreate) -> Comment:
        '''
        Crea un nuevo comentario validando:
        1. Longitud del contenido (5-200 caracteres)
        2. Existencia del user_id y trip_id en la BD
        '''
        # Validar longitud del contenido
        self.validate_comment_length(comment_in.content)
        
        # VALIDAR FOREIGN KEYS: Verificar que user_id existe
        if not self.user_repo.get_by_id(comment_in.user_id):
            raise AppError(404, ErrorCode.USER_NOT_FOUND, f"El usuario con ID {comment_in.user_id} no existe")
        
        # VALIDAR FOREIGN KEYS: Verificar que trip_id existe
        if not self.trip_repo.get_by_id(comment_in.trip_id):
            raise AppError(404, ErrorCode.TRIP_NOT_FOUND, f"El viaje con ID {comment_in.trip_id} no existe")
        
        # Crear comentario después de validaciones
        comment = Comment(**comment_in.model_dump())
        return self.repo.create(comment)

    @transactional
    def update(self, comment_id: int, comment_in: CommentUpdate) -> Comment:
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise AppError(404, ErrorCode.COMMENT_NOT_FOUND, "El comentario no existe")
        
        # Convertir a dict solo con campos no-None
        comment_data = comment_in.model_dump(exclude_unset=True)
        
        # Validar longitud si se está actualizando
        if 'content' in comment_data and comment_data['content'] is not None:
            self.validate_comment_length(comment_data['content'])
        
        return self.repo.update(comment, comment_data)

    @transactional
    def delete(self, comment_id: int) -> None:
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise AppError(404, ErrorCode.COMMENT_NOT_FOUND, "El comentario no existe")

        self.repo.delete(comment)