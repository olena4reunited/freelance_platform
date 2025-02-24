from typing import Callable, Any
from functools import wraps

from fastapi import HTTPException
from fastapi.exceptions import ResponseValidationError
from psycopg2.errors import DatabaseError, OperationalError, IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse


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
            status_code: int,
            detail: str | None = None,
            extra: dict | None = None
    ) -> JSONResponse:
        raise cls(status_code=status_code, detail=detail, extra=extra)

    @classmethod
    def catcher(cls, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                cls.raise_exception(
                    500,
                    "Database integrity error",
                    extra={"pgerror": str(e)}
                )
            except (DatabaseError, OperationalError) as e:
                cls.raise_exception(
                    500,
                    "Database error",
                    extra={"pgerror": str(e)}
                )
            except ResponseValidationError as e:
                cls.raise_exception(
                    501,
                    "Service Not implemented",
                    extra={"error": str(e)}
                )
            except HTTPException as e:
                raise e
            except Exception as e:
                cls.raise_exception(
                    501,
                    "Service Not implemented",
                    extra={"error": str(e)}
                )
        return wrapper


async def custom_exception_handler(request: Request, exc: CustomHTTPException) -> JSONResponse | None:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    return JSONResponse(
        status_code=501,
        content={
            "status_code": 501,
            "detail": "Service not implemented or do not exist anymore",
            "extra": {"request": str(request.path_params)},
        },
    )
