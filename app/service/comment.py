from sqlalchemy.orm import Session
from app.db.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from app.core.exceptions import AppError


def get_all_comments(db: Session) -> list[Comment]:
    return db.query(Comment).all()

def get_comment_by_id(db: Session, id: int) -> Comment | None:
    return db.query(Comment).filter(Comment.id == id).first()

def get_comments_by_trip_id(db: Session, trip_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.trip_id == trip_id).all()

def get_comments_by_user_id(db: Session, user_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.user_id == user_id).all()

def validate_comment_length(content: str) -> None:
    """Valida longitud del contenido del comentario"""
    if len(content) < 5:
        raise AppError(400, "COMMENT_TOO_SHORT", "El comentario debe tener al menos 5 caracteres")
    if len(content) > 200:
        raise AppError(400, "COMMENT_TOO_LONG", "El comentario no puede tener más de 200 caracteres")

def create_comment(db: Session, comment_in: CommentCreate) -> Comment:
    # Validar longitud del contenido (también validado en schema, pero mantenemos por si acaso)
    validate_comment_length(comment_in.content)
    
    # Crear comentario después de validaciones
    comment = Comment(**comment_in.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def update_comment(db: Session, comment_id: int, comment_in: CommentUpdate) -> Comment:
    # Reutilizar get_comment_by_id
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")
    
    # Convertir a dict solo con campos no-None
    comment_data = comment_in.model_dump(exclude_unset=True)
    
    # Validar longitud si se está actualizando
    if 'content' in comment_data and comment_data['content'] is not None:
        validate_comment_length(comment_data['content'])
    
    # Actualizar solo campos no-None
    for key, value in comment_data.items():
        if value is not None:
            setattr(comment, key, value)
    
    db.commit()
    db.refresh(comment)
    return comment    

def delete_comment(db: Session, comment_id: int) -> None:
    # Reutilizar get_comment_by_id
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")

    db.delete(comment)
    db.commit()