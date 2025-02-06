from enum import Enum

from pydantic import BaseModel


class PlanEnum(Enum):
    admin = 1
    moderator = 2
    customer = 3
    performer = 4