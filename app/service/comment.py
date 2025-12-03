from sqlalchemy.orm import Session
from app.db.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentDelete
from app.core.exceptions import AppError


def get_all_comments(db: Session) -> list[Comment]:
    return db.query(Comment).all()

def get_comment_by_id(db: Session, id: int) -> Comment | None:
    return db.query(Comment).filter(Comment.id == id).first()

def get_comments_by_trip_id(db: Session, trip_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.trip_id == trip_id).all()

def get_comments_by_user_id(db: Session, user_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.user_id == user_id).all()

def create_comment(db: Session, comment_in: CommentCreate) -> Comment:

    comment_long_error(comment_in.content)
    
    comment = Comment(**comment_in.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def update_comment(db: Session, comment_id: int, comment_in: CommentUpdate) -> Comment:
    comment = get_comment_by_id(db, comment_id)

    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")
    
    for key, value in comment_in.model_dump().items():
        setattr(comment, key, value)

    comment_long_error(comment_in.content)
    
    db.commit()
    db.refresh(comment)
    return comment    

def comment_long_error(content: str) -> None:
    
    if (len(content) > 200):
        raise AppError(400, "COMMENT_TOO_LONG", "El comentario no puede tener más de 200 caracteres")
    
    if (len(content) < 5):
        raise AppError(400, "COMMENT_TOO_SHORT", "El comentario no puede tener menos de 5 caracteres")
    
    return None

def delete_comment(db: Session, comment_id: int) -> None:
    comment = get_comment_by_id(db, comment_id)

    db.delete(comment)
    db.commit()
    return None