from functools import wraps
from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.core.constants import ErrorCode

def transactional(func):
    """
    Decorador para manejar transacciones de base de datos automáticamente.
    Realiza commit si todo va bien, y rollback si ocurre una excepción.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Buscar el objeto db (Session) en los argumentos
        db = None
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if not db and 'db' in kwargs:
            db = kwargs['db']
            
        if not db:
            # Si no encontramos la sesión, ejecutamos la función normalmente
            # (esto no debería pasar si se usa correctamente)
            return func(*args, **kwargs)
            
        try:
            result = func(*args, **kwargs)
            db.commit()
            if hasattr(result, "__dict__"):
                db.refresh(result)
            return result
        except AppError:
            # Si es un error de aplicación ya controlado, solo hacemos rollback y re-lanzamos
            db.rollback()
            raise
        except Exception as e:
            # Si es un error inesperado, hacemos rollback y lanzamos AppError 500
            db.rollback()
            raise AppError(500, ErrorCode.INTERNAL_SERVER_ERROR, str(e))
            
    return wrapper
