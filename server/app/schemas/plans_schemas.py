from pydantic import BaseModel


class PlanBase(BaseModel):
    name: str
