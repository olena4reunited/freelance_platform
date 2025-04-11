import json
from functools import wraps

from server.app.utils.redis_client import redis_client


def required_permissions(permissions: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_plan = kwargs.get("context").invocation_metadata.get("user_plan")
            
            if not user_plan:
                raise ValueError("User not found in kwargs")

            user_permissions = set(json.loads(redis_client.hgetall(user_plan).get("permissions")))

            if not all(perm in user_permissions for perm in permissions):
                raise ValueError("User does not have the required permissions")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
