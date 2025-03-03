from typing import Any

from server.app.models.users_profile_feedback_model import UserProfileFeedback


class ProfileFeedbackController:
    @staticmethod
    def create_feedback(
            user_id: int,
            commentator_id: int,
            feedback: dict[str, Any]
    ) -> dict[str, Any] | None:
        return UserProfileFeedback.create_feedback(
            user_id,
            commentator_id,
            feedback
        )

    @staticmethod
    def get_all_feedback_own_profile(user_id: int) -> dict[str, Any] | None:
        return UserProfileFeedback.get_all_user_feedback(user_id)

    @staticmethod
    def get_feedback_details_own_profile(
            feedback_id: int,
            user_id: int
    ) -> dict[str, Any] | None:
        return UserProfileFeedback.get_user_feedback(feedback_id)
