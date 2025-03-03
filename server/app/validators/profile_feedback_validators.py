from server.app.utils.exceptions import GlobalException
from server.app.models.users_profile_feedback_model import UserProfileFeedback


class ProfileFeedbackValidator:
    def __init__(self, user_id: int, feedback_id: int):
        self.user_id = user_id
        self.feedback_id = feedback_id

    def validate_feedback_user_profile(self):
        feedback = UserProfileFeedback.get_record_by_id(self.feedback_id)

        if not feedback:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=404,
                detail="Requested feedback was not found"
            )
        if feedback.get("profile_id") != self.user_id:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=403,
                detail="Requested feedback was forbidden to detail access for current user"
            )

        return self
