from typing import Callable
from functools import wraps

from fastapi import HTTPException
from starlette import status
from psycopg2.errors import DatabaseError, OperationalError, IntegrityError


class CustomHTTPException(HTTPException):
    def __init__(
            self,
            status_code: int,
            detail: str | None = None,
            headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )

    @classmethod
    def bad_request(cls, detail: str = "Bad request") -> None:
        raise cls(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    @classmethod
    def unauthorised(cls, detail: str = "Unauthorised") -> None:
        raise cls(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    @classmethod
    def forbidden(cls, detail: str = "Forbidden") -> None:
        raise cls(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    @classmethod
    def not_found(cls, detail: str = "Not found") -> None:
        raise cls(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    @classmethod
    def internal_server_error(cls, detail: str = "Internal server error") -> None:
        raise cls(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    @classmethod
    def service_unavailable(cls, detail: str = "Service unavailable") -> None:
        raise cls(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)

    @classmethod
    def gateway_timeout(cls, detail: str = "Gateway timeout") -> None:
        raise cls(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=detail)


def handle_db_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            CustomHTTPException.bad_request(detail=f"Database integrity error: {e.pgerror}")
        except (DatabaseError, OperationalError) as e:
            CustomHTTPException.internal_server_error(detail=f"Internal server error: {e.pgerror}")
        except Exception as e:
            raise e
    return wrapper
