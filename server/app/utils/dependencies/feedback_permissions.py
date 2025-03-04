from functools import wraps
from typing import Callable
import json

from server.app.utils.redis_client import redis_client
from server.app.utils.exceptions import GlobalException
from server.app.validators.profile_feedback_validators import ProfileFeedbackValidator


def can_delete_feedback():
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            feedback_id = kwargs.get("feedback_id")
            user = kwargs.get("user")

            user_plan = user.get("plan_name")
            user_permissions = set(json.loads(redis_client.hgetall(user_plan).get("permissions")))

            if not user_plan:
                GlobalException.CustomHTTPException.raise_exception(
                    status_code=403,
                    detail="User plan not found",
                )
            if user_plan in ["customer", "performer"]:
                if not {"update_feedback_info_created_by_current_user", "delete_feedback_created_by_current_user"}.issubset(
                        user_permissions):
                    GlobalException.CustomHTTPException.raise_exception(
                        status_code=403,
                        detail="User does not have permission to access resource"
                    )
                ProfileFeedbackValidator(
                    user_id=user.get("id"),
                    feedback_id=feedback_id,
                ). \
                validate_feedback_commentator()
            if user_plan in ["admin", "moderator"]:
                if not {"read_feedbacks_details_selected_user", "delete_feedback_selected_user"}.issubset(user_permissions):
                    GlobalException.CustomHTTPException.raise_exception(
                        status_code=403,
                        detail="User does not have permission to access resource"
                    )

            ProfileFeedbackValidator(
                user_id=user_id,
                feedback_id=feedback_id,
            ). \
            validate_feedback_user_profile()

            return func(*args, **kwargs)
        return wrapper
    return decorator
