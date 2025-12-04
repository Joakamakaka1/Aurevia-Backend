from sqlalchemy.orm import Session
from app.db.models.comment import Comment
from typing import List, Optional

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Comment]:
        return self.db.query(Comment).all()

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def get_by_trip_id(self, trip_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.trip_id == trip_id).all()

    def get_by_user_id(self, user_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.user_id == user_id).all()

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        return comment

    def update(self, comment: Comment, comment_data: dict) -> Comment:
        for key, value in comment_data.items():
            if value is not None:
                setattr(comment, key, value)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
