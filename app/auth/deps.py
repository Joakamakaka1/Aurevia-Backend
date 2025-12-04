# ============================================================================
# TEMPORAL. CAMBIAR POR JWT
# ============================================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.service.user import UserService
from app.auth.security import verify_password

security = HTTPBasic()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_basic(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Usar UserService en lugar de la función get_by_email
    user_service = UserService(db)
    user = user_service.get_by_email(credentials.username)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        # Importante: cabecera WWW-Authenticate para que el cliente sepa que es Basic
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user
