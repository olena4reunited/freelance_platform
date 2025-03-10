from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    sender_id: int
    content: str
    created_at: datetime
