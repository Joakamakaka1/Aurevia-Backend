from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class AppError(Exception):

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}, "details": None}
    )

# Convertir 422 de Pydantic a 400 Bad Request
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "BAD_REQUEST", "message": "Datos inválidos en la petición"}, "details": exc.errors()}
    )

# 500 genérico para lo no controlado
async def unhandled_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "SERVER_ERROR", "message": "Error interno del servidor"}, "details": str(exc)}
    )
