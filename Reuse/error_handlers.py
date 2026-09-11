from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from exceptions import ValidationError, AuthError, DatabaseError

def register_error_handlers(app):

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": exc.message,
                    "status_code": 400
                }
            }
        )

    @app.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc: AuthError):
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "type": "AuthError",
                    "message": exc.message,
                    "status_code": 401
                }
            }
        )

    @app.exception_handler(DatabaseError)
    async def db_error_handler(request: Request, exc: DatabaseError):
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "DatabaseError",
                    "message": exc.message,
                    "status_code": 500
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def pydantic_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "SchemaValidationError",
                    "message": exc.errors(),
                    "status_code": 422
                }
            }
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            }
        )
