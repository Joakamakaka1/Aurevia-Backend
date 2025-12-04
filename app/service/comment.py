from sqlalchemy.orm import Session
from app.db.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.comment import CommentRepository
from app.service.user import get_user_by_id
from app.service.trip import get_trip_by_id

def get_all_comments(db: Session) -> list[Comment]:
    repo = CommentRepository(db)
    return repo.get_all()

def get_comment_by_id(db: Session, id: int) -> Comment | None:
    repo = CommentRepository(db)
    return repo.get_by_id(id)

def get_comments_by_trip_id(db: Session, trip_id: int) -> list[Comment]:
    repo = CommentRepository(db)
    return repo.get_by_trip_id(trip_id)

def get_comments_by_user_id(db: Session, user_id: int) -> list[Comment]:
    repo = CommentRepository(db)
    return repo.get_by_user_id(user_id)

def validate_comment_length(content: str) -> None:
    """Valida longitud del contenido del comentario"""
    if len(content) < 5:
        raise AppError(400, ErrorCode.COMMENT_TOO_SHORT, "El comentario debe tener al menos 5 caracteres")
    if len(content) > 200:
        raise AppError(400, ErrorCode.COMMENT_TOO_LONG, "El comentario no puede tener más de 200 caracteres")

@transactional
def create_comment(db: Session, comment_in: CommentCreate) -> Comment:
    repo = CommentRepository(db)
    
    # Validar longitud del contenido (también validado en schema, pero mantenemos por si acaso)
    validate_comment_length(comment_in.content)
    
    # VALIDAR FOREIGN KEYS: Verificar que user_id existe
    if not get_user_by_id(db, comment_in.user_id):
        raise AppError(404, ErrorCode.USER_NOT_FOUND, f"El usuario con ID {comment_in.user_id} no existe")
    
    # VALIDAR FOREIGN KEYS: Verificar que trip_id existe
    if not get_trip_by_id(db, comment_in.trip_id):
        raise AppError(404, ErrorCode.TRIP_NOT_FOUND, f"El viaje con ID {comment_in.trip_id} no existe")
    
    # Crear comentario después de validaciones
    comment = Comment(**comment_in.model_dump())
    return repo.create(comment)

@transactional
def update_comment(db: Session, comment_id: int, comment_in: CommentUpdate) -> Comment:
    repo = CommentRepository(db)
    comment = repo.get_by_id(comment_id)
    if not comment:
        raise AppError(404, ErrorCode.COMMENT_NOT_FOUND, "El comentario no existe")
    
    # Convertir a dict solo con campos no-None
    comment_data = comment_in.model_dump(exclude_unset=True)
    
    # Validar longitud si se está actualizando
    if 'content' in comment_data and comment_data['content'] is not None:
        validate_comment_length(comment_data['content'])
    
    return repo.update(comment, comment_data)

@transactional
def delete_comment(db: Session, comment_id: int) -> None:
    repo = CommentRepository(db)
    comment = repo.get_by_id(comment_id)
    if not comment:
        raise AppError(404, ErrorCode.COMMENT_NOT_FOUND, "El comentario no existe")

    repo.delete(comment)