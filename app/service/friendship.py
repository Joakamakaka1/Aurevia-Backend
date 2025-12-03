# from sqlalchemy.orm import Session
# from app.db.models.friendship import Friendship
# from app.core.exceptions import AppError
# from app.schemas.friendship import FriendshipCreate, FriendshipUpdate

# def get_all_friendships(db: Session) -> list[Friendship]:
#     return db.query(Friendship).all()

# def get_friendship_by_id(db: Session, friendship_id: int) -> Friendship | None:
#     return db.query(Friendship).filter(Friendship.id == friendship_id).first() 

# def create_friendship(db: Session, friend_in: FriendshipCreate) -> Friendship:
#     if(friend_in.user_id == friend_in.friend_id):
#         raise AppError(400, "SAME_USER", "You can't be friends with yourself")
    
#     if(get_friendship_by_id(db, friend_in.user_id) or get_friendship_by_id(db, friend_in.friend_id)):
#         raise AppError(400, "FRIENDSHIP_ALREADY_EXISTS", "You are already friends with this user")
    
#     friend = Friendship(**friend_in.model_dump())
#     db.add(friend)
#     db.commit()
#     db.refresh(friend)
#     return friend

# # TODO: Implementar logica 
# def update_friendship(db: Session, friend_in: FriendshipUpdate) -> Friendship:
#     pass

# def delete_friendship(db: Session, *, friendship_id: int) -> None:
#     db.query(Friendship).filter(Friendship.id == friendship_id).delete()
#     db.commit()