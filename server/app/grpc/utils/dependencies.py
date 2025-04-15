import json
from functools import wraps

import grpc

from server.app.utils.redis_client import redis_client
from server.app.grpc.utils.context import user_plan_var
from server.app.utils.logger import logger


def required_permissions(permissions: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, request, context: grpc.aio.ServicerContext, *args, **kwargs):
            user_plan = user_plan_var.get()

            if not user_plan:
                logger.error("User plan not found in context. Performance action aborted.")
                await context.abort(grpc.StatusCode.UNAUTHENTICATED, "User not authenticated or context missing.")

            user_permissions = set(json.loads(redis_client.hgetall(user_plan).get("permissions")))

            if not all(perm in user_permissions for perm in permissions):
                logger.error("User does not have required permissions. Performance action aborted.")
                await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied.")
            
            return await func(self, request, context, *args, **kwargs)
        return wrapper
    return decorator
