from sqlalchemy.orm import Session, joinedload
from app.db.models.user import User
from app.schemas.user import UserCreate
from typing import List, Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.trips), joinedload(User.comments))
            .all()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.trips), joinedload(User.comments))
            .filter(User.email == email)
            .first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.trips), joinedload(User.comments))
            .filter(User.username == username)
            .first()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.trips), joinedload(User.comments))
            .filter(User.id == user_id)
            .first()
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
