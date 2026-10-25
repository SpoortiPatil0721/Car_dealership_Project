from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BadRequestError(AppError):
    status_code = 400


class AuthenticationError(AppError):
    status_code = 401


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class OutOfStockError(ConflictError):
    pass


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
