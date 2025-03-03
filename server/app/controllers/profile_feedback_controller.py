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
    def get_all_user_feedback(user_id: int) -> dict[str, Any] | None:
        return UserProfileFeedback.get_all_user_feedback(user_id)

    @staticmethod
    def get_feedback_details_own_profile(feedback_id: int) -> dict[str, Any] | None:
        return UserProfileFeedback.get_user_feedback(feedback_id)

    @staticmethod
    def update_feedback(
            feedback_id: int,
            feedback: dict[str, Any]
    ) -> dict[str, Any] | None:
        return UserProfileFeedback.update_user_profile_feedback(
            feedback_id,
            feedback
        )

    @staticmethod
    def delete_feedback(
            user_id: int,
            feedback_id: int
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        UserProfileFeedback.delete_record_by_id(feedback_id)

        return UserProfileFeedback.get_all_user_feedback(user_id)
