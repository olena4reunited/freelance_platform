import asyncio
from typing import Callable, Any, Awaitable
from functools import wraps
import traceback

import grpc

from fastapi import HTTPException
from fastapi.exceptions import ResponseValidationError, ValidationException
from psycopg2.errors import DatabaseError, OperationalError, IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse

from server.app.utils.logger import logger


def get_http_error_code(status_code: grpc.StatusCode) -> int:
    mapping = {
        grpc.StatusCode.OK: 200,
        grpc.StatusCode.INVALID_ARGUMENT: 400,
        grpc.StatusCode.UNAUTHENTICATED: 401,
        grpc.StatusCode.PERMISSION_DENIED: 403,
        grpc.StatusCode.NOT_FOUND: 404,
        grpc.StatusCode.ALREADY_EXISTS: 409,
        grpc.StatusCode.INTERNAL: 500,
        grpc.StatusCode.UNIMPLEMENTED: 501,
        grpc.StatusCode.UNKNOWN: 502,
        grpc.StatusCode.UNAVAILABLE: 503,
    }
    return mapping.get(status_code, 502)


class GlobalException(Exception):
    @classmethod
    def catcher(cls, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Exception:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            except (grpc.aio.AioRpcError, grpc.aio.AbortError) as e:
                logger.error(
                    "gRPC error was occured: \n%s" \
                    "\x1b[31mERROR TRACEBACK:\x1b[0m\n%s",
                    " "*10,
                    traceback.format_exc()
                )
                raise GlobalException.CustomHTTPException(
                    status_code=get_http_error_code(e.code()),
                    detail=e.details()
                )
            except (DatabaseError, OperationalError, IntegrityError) as e:
                logger.error(
                    "Database error was occured: \n%s\x1b[31m" \
                    "ERROR TRACEBACK:\x1b[0m\n%s",
                    " "*10,
                    traceback.format_exc()
                )
                GlobalException.CustomHTTPException.raise_exception(
                    500,
                    "Database error",
                    extra={"error": str(e)}
                )
            except HTTPException as e:
                logger.error(
                    "Error was occured: \n%s\x1b[31m" \
                    "ERROR TRACEBACK:\x1b[0m\n%s",
                    " "*10,
                    traceback.format_exc()
                )
                GlobalException.CustomHTTPException.raise_exception(
                    e.status_code,
                    e.detail,
                    extra={"error": str(e)}
                )
            except Exception as e:
                logger.error(
                    "Error was occured: \n%s\x1b[31m" \
                    "ERROR TRACEBACK:\x1b[0m\n%s",
                    " "*10,
                    traceback.format_exc()
                )
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
