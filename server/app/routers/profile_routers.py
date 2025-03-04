from typing import Any, Union
import json

from fastapi import APIRouter, Depends

from server.app.schemas.profile_feedback_schemas import (
    ProfileFeedbackCreate,
    ProfileFeedbackUpdate,
    ProfileFeedbackResponse
)
from server.app.controllers.profile_feedback_controller import ProfileFeedbackController
from server.app.validators.profile_feedback_validators import ProfileFeedbackValidator
from server.app.utils.exceptions import GlobalException
from server.app.utils.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)
from server.app.utils.redis_client import redis_client


router = APIRouter(prefix="/profile", tags=["feedback"])


@router.get("/me/feedback", response_model=Union[list[ProfileFeedbackResponse], ProfileFeedbackResponse])
@GlobalException.catcher
@required_plans(["customer", "performer"])
@required_permissions(["read_all_feedbacks_own_profile"])
def read_your_feedbacks(
        user: dict[str, Any] = Depends(get_current_user),
):
    return ProfileFeedbackController.get_all_user_feedback(user.get("id"))


@router.get("/me/feedback/{feedback_id}", response_model=ProfileFeedbackResponse)
@GlobalException.catcher
@required_plans(["customer", "performer"])
@required_permissions(["read_all_feedbacks_own_profile", "read_feedback_details_own_profile"])
def read_your_feedbacks_details(
        feedback_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    ProfileFeedbackValidator(
        user_id=user.get("id"),
        feedback_id=feedback_id,
    ). \
    validate_feedback_user_profile()

    return ProfileFeedbackController.get_feedback_details(feedback_id)


@router.get("/{user_id}/feedback", response_model=Union[list[ProfileFeedbackResponse], ProfileFeedbackResponse])
@GlobalException.catcher
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_all_feedbacks_selected_user"])
def read_user_feedbacks(
        user_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    return ProfileFeedbackController.get_all_user_feedback(user_id)


@router.post("/{user_id}/feedback", response_model=ProfileFeedbackResponse)
@GlobalException.catcher
@required_plans(["customer", "performer"])
@required_permissions(["send_feedback"])
def send_feedback(
        user_id: int,
        feedback_data: ProfileFeedbackCreate,
        user: dict[str, Any] = Depends(get_current_user),
):
    return ProfileFeedbackController.create_feedback(
        user_id=user_id,
        commentator_id=user.get("id"),
        feedback=feedback_data.model_dump(),
    )


@router.patch("/{user_id}/feedback/{feedback_id}", response_model=ProfileFeedbackResponse)
@GlobalException.catcher
@required_plans(["customer", "performer"])
@required_permissions(["update_feedback_info_created_by_current_user"])
def update_feedback(
        user_id: int,
        feedback_id: int,
        feedback_data: ProfileFeedbackUpdate,
        user: dict[str, Any] = Depends(get_current_user),
):
    ProfileFeedbackValidator(
        user_id=user.get("id"),
        feedback_id=feedback_id,
    ). \
    validate_feedback_commentator()

    return ProfileFeedbackController.update_feedback(feedback_id, feedback_data.model_dump())


@router.delete("/{user_id}/feedback/{feedback_id}", response_model=Union[list[ProfileFeedbackResponse], ProfileFeedbackResponse])
@GlobalException.catcher
@required_plans(["admin", "moderator", "customer", "performer"])
def delete_feedback(
        user_id: int,
        feedback_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    try:
        user_plan = user.get("plan")
        user_permissions = set(json.loads(redis_client.hgetall(user_plan).get("permissions")))

        if not user_plan:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="User plan not found",
            )
        if user_plan in ["customer", "performer"]:
            if not {"update_feedback_info_created_by_current_user", "delete_feedback_created_by_current_user"}.issubset(user_permissions):
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
    except GlobalException.CustomHTTPException as e:
        if e.status_code == 404:
            pass
        raise e
    finally:
        return ProfileFeedbackController.delete_feedback(user_id=user_id, feedback_id=feedback_id)


@router.get("/{user_id}/feedback/{feedback_id}", response_model=ProfileFeedbackResponse)
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_feedbacks_selected_user", "read_feedbacks_details_selected_user"])
def read_user_feedback_details(
        user_id: int,
        feedback_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    ProfileFeedbackValidator(
        user_id=user_id,
        feedback_id=feedback_id,
    ). \
    validate_feedback_user_profile()

    return ProfileFeedbackController.get_feedback_details(feedback_id)
