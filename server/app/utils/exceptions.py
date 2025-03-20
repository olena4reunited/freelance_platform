from typing import Callable, Any, Awaitable
from functools import wraps

from fastapi import HTTPException
from fastapi.exceptions import ResponseValidationError, ValidationException
from psycopg2.errors import DatabaseError, OperationalError, IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse


class GlobalException(Exception):
    @classmethod
    def catcher(cls, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Exception:
            try:
                if isinstance(func, Awaitable):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            except (DatabaseError, OperationalError, IntegrityError) as e:
                GlobalException.CustomHTTPException.raise_exception(
                    500,
                    "Database error",
                    extra={"error": str(e)}
                )
            except HTTPException as e:
                GlobalException.CustomHTTPException.raise_exception(
                    e.status_code,
                    e.detail,
                    extra={"error": str(e)}
                )
            except Exception as e:
                GlobalException.CustomHTTPException.raise_exception(
                    501,
                    "Service not implemented or do not exist anymore",
                    extra={"error": str(e)}
                )

        return wrapper

    class CustomHTTPException(HTTPException):
        def __init__(
                self,
                status_code: int,
                detail: str | None = None,
                extra: dict | None = None
        ) -> None:
            super().__init__(status_code=status_code, detail=detail)
            self.extra = extra

        def to_dict(self):
            return {
                "status_code": self.status_code,
                "detail": self.detail,
                "extra": self.extra,
            }

        @classmethod
        def raise_exception(
                cls,
                status_code: int = 501,
                detail: str | None = None,
                extra: dict | None = None
        ) -> Exception:
            raise cls(status_code=status_code, detail=detail, extra=extra)


async def global_exception_handler(request: Request, exc: GlobalException.CustomHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "status_code": 501,
            "detail": "Service not implemented or do not exist anymore",
            "extra": {"request": str(request.path_params)},
        },
    )
