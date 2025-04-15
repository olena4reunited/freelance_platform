from functools import wraps

import grpc

from server.app.utils.logger import logger
from server.app.utils.exceptions import GlobalException


def get_grpc_error_code(status_code: int) -> grpc.StatusCode:
    mapping = {
        200: grpc.StatusCode.OK,
        201: grpc.StatusCode.OK,
        204: grpc.StatusCode.OK,
        400: grpc.StatusCode.INVALID_ARGUMENT,
        401: grpc.StatusCode.UNAUTHENTICATED,
        403: grpc.StatusCode.PERMISSION_DENIED,
        404: grpc.StatusCode.NOT_FOUND,
        409: grpc.StatusCode.ALREADY_EXISTS,
        422: grpc.StatusCode.INVALID_ARGUMENT,
        500: grpc.StatusCode.INTERNAL,
        501: grpc.StatusCode.UNIMPLEMENTED,
        502: grpc.StatusCode.UNKNOWN,
        503: grpc.StatusCode.UNAVAILABLE
    }
    return mapping.get(status_code, grpc.StatusCode.UNKNOWN)


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(self, request, context: grpc.aio.ServicerContext, *args, **kwargs):
        try:
            return await func(self, request, context, *args, **kwargs)
        except GlobalException.CustomHTTPException as e:
            logger.error(f"Error was occured: {e.detail}")
            await context.abort(get_grpc_error_code(e.status_code), str(e.detail))
        except grpc.aio.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            await context.abort(e.code(), e.details())
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await context.abort(grpc.StatusCode.UNKNOWN, str(e))
    return wrapper
