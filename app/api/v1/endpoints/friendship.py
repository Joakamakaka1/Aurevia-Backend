# from fastapi import APIRouter, Depends, Response, status
# from typing import List
# from sqlalchemy.orm import Session
# from app.auth.deps import get_db
# from app.service import friendship as crud_friendship
# from app.schemas.friendship import *


# router = APIRouter(prefix="/v1/friendship", tags=["Friendship"])

# @router.get("/", response_model=List[FriendshipOut], status_code=status.HTTP_200_OK)
# def get_all_friendships(db: Session = Depends(get_db)):
#     return crud_friendship.get_all_friendships(db)

# @router.get("/{id}", response_model=FriendshipOut, status_code=status.HTTP_200_OK)
# def get_friendship_by_id(id: int, db: Session = Depends(get_db)):
#     return crud_friendship.get_friendship_by_id(db, id)

# @router.post("/", response_model=FriendshipOut, status_code=status.HTTP_201_CREATED)
# def create_friendship(payload: FriendshipCreate, db: Session = Depends(get_db)):
#     return crud_friendship.create(db, friendship_in=payload)
# # TODO
# @router.put("/{id}", response_model=FriendshipOut, status_code=status.HTTP_200_OK)
    
# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_friendship(id: int, db: Session = Depends(get_db)):
#     crud_friendship.delete(db, friendship_id=id)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)