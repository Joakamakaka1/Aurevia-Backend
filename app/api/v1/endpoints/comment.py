from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import comment as crud_comment
from app.schemas.comment import *

router = APIRouter(prefix="/v1/comment", tags=["Comment"])

@router.get("/", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_all_comments(db: Session = Depends(get_db)):
    return crud_comment.get_all_comments(db)

@router.get("/{id}", response_model=CommentOut, status_code=status.HTTP_200_OK)
def get_comment_by_id(id: int, db: Session = Depends(get_db)):
    return crud_comment.get_comment_by_id(db, id)

@router.get("/user/{user_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments_by_user_id(user_id: int, db: Session = Depends(get_db)):
    return crud_comment.get_comments_by_user_id(db, user_id)

@router.get("/trip/{trip_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments_by_trip_id(trip_id: int, db: Session = Depends(get_db)):
    return crud_comment.get_comments_by_trip_id(db, trip_id)

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db)):
    return crud_comment.create_comment(db, comment_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id: int, db: Session = Depends(get_db)):
    crud_comment.delete_comment(db, comment_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)