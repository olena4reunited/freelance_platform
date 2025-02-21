from datetime import datetime

from pydantic import BaseModel


class BlockRequest(BaseModel):
    block_timestamp: datetime
