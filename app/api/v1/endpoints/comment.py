from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import comment as crud_comment
from app.schemas.comment import *
from app.core.exceptions import AppError

router = APIRouter(prefix="/v1/comment", tags=["Comment"])

@router.get("/", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_all_comments(db: Session = Depends(get_db)):
    return crud_comment.get_all_comments(db)

@router.get("/{id}", response_model=CommentOut, status_code=status.HTTP_200_OK)
def get_comment_by_id(id: int, db: Session = Depends(get_db)):
    comment = crud_comment.get_comment_by_id(db, id)
    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")
    return comment

@router.get("/user/{user_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments_by_user(user_id: int, db: Session = Depends(get_db)):
    comments = crud_comment.get_comments_by_user_id(db, user_id)
    return comments

@router.get("/trip/{trip_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments_by_trip(trip_id: int, db: Session = Depends(get_db)):
    comments = crud_comment.get_comments_by_trip_id(db, trip_id)
    return comments

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db)):
    return crud_comment.create_comment(db, comment_in=payload)

@router.put("/{id}", response_model=CommentOut, status_code=status.HTTP_200_OK)
def update_comment(id: int, payload: CommentUpdate, db: Session = Depends(get_db)):
    return crud_comment.update_comment(db, comment_id=id, comment_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id: int, db: Session = Depends(get_db)):
    crud_comment.delete_comment(db, comment_id=id)
