from pydantic import BaseModel, conint


class ProfileFeedbackCreate(BaseModel):
    content: str | None = None
    rate: conint(ge=0, le=5)
    image_link: str | None = None


class ProfileFeedbackUpdate(BaseModel):
    content: str | None = None
    rate: conint(ge=0, le=5) | None = None
    image_link: str | None = None


class ProfileFeedbackResponse(BaseModel):
    id: int
    content: str | None = None
    rate: conint(ge=0, le=5)
    commentator_id: int | None = None
    profile_id: int
    image_link: str | None = None
