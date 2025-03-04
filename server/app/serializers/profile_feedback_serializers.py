from typing import Any

from server.app.schemas.profile_feedback_schemas import ProfileFeedbackResponse, CommentatorBase


def serialize_profile_feedback(feedback: dict[str, Any]) -> ProfileFeedbackResponse:
    return ProfileFeedbackResponse(
        id=feedback.get("id"),
        content=feedback.get("content"),
        rate=feedback.get("rate"),
        commentator=CommentatorBase(
            username=feedback.get("commentator_username"),
            photo_link=feedback.get("commentator_photo_link"),
        ),
        profile_id=feedback.get("profile_id"),
        image_link=feedback.get("image_link"),
    )
