import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    sender_id: int
    content: str
    image_ids: list[int] | None = None
    created_at: datetime.datetime
