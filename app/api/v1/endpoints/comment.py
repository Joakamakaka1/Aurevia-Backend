from fastapi import APIRouter, Depends, status
from typing import List
from app.service.comment import CommentService
from app.schemas.comment import *
from app.core.exceptions import AppError
from app.api.deps import get_comment_service
from app.auth.deps import get_current_user, check_self_or_admin

router = APIRouter(prefix="/v1/comment", tags=["Comment"])

@router.get("/", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_all_comments(
    skip: int = 0,
    limit: int = 50,
    service: CommentService = Depends(get_comment_service)
):
    return service.get_all(skip=skip, limit=limit)

@router.get("/{id}", response_model=CommentOut, status_code=status.HTTP_200_OK)
def get_comment_by_id(id: int, service: CommentService = Depends(get_comment_service)):
    comment = service.get_by_id(id)
    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")
    return comment

@router.get("/trip/{trip_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments_by_trip(trip_id: int, service: CommentService = Depends(get_comment_service)):
    return service.get_by_trip_id(trip_id)

@router.get("/user/{user_id}", response_model=List[CommentOut], status_code=status.HTTP_200_OK)
def get_comments_by_user(user_id: int, service: CommentService = Depends(get_comment_service)):
    return service.get_by_user_id(user_id)

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate, 
    service: CommentService = Depends(get_comment_service),
    current_user = Depends(get_current_user)
):
    # Forzar que el usuario que crea el comentario sea el mismo del token
    # Evita spoofing de identidad
    if payload.user_id != current_user.user_id:
        payload.user_id = current_user.user_id

    return service.create(comment_in=payload)

@router.put("/{id}", response_model=CommentOut, status_code=status.HTTP_200_OK)
def update_comment(
    id: int, 
    payload: CommentUpdate, 
    service: CommentService = Depends(get_comment_service),
    current_user = Depends(get_current_user)
):
    comment = service.get_by_id(id)
    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")
        
    # Validar que sea dueño o admin
    check_self_or_admin(current_user, comment.user_id)
    
    return service.update(comment_id=id, comment_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    id: int, 
    service: CommentService = Depends(get_comment_service),
    current_user = Depends(get_current_user)
):
    comment = service.get_by_id(id)
    if not comment:
        raise AppError(404, "COMMENT_NOT_FOUND", "El comentario no existe")
        
    # Validar que sea dueño o admin
    check_self_or_admin(current_user, comment.user_id)
    
    service.delete(comment_id=id)
