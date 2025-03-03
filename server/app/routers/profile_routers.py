from typing import Any, Union

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

    return ProfileFeedbackController.get_feedback_details_own_profile(feedback_id)


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
@required_plans(["customer", "performer"])
@required_permissions(["update_feedback_info_created_by_current_user", "delete_feedback_created_by_current_user"])
def delete_feedback(
        user_id: int,
        feedback_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    ProfileFeedbackValidator(
        user_id=user.get("id"),
        feedback_id=feedback_id,
    ). \
    validate_feedback_commentator()

    ProfileFeedbackValidator(
        user_id=user_id,
        feedback_id=feedback_id,
    ). \
    validate_feedback_user_profile()

    return ProfileFeedbackController.delete_feedback(feedback_id)


@router.get("/{user_id}/feedback/{feedback_id}", response_model=ProfileFeedbackResponse)
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_feedbacks_selected_user", "read_feedbacks_details_selected_user"])
def read_user_feedback_details(
        user_id: int,
        feedback_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    ...


@router.delete("/{user_id}/feedback/{feedback_id}", response_model=ProfileFeedbackResponse)
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_feedbacks_details_selected_user", "delete_feedback_selected_user"])
def update_feedback(
        user_id: int,
        feedback_id: int,
        user: dict[str, Any] = Depends(get_current_user),
):
    ...
