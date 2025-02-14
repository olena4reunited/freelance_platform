from pydantic import BaseModel


class PlanCreate(BaseModel):
    plan: str


class PlanUpdate(PlanCreate):
    pass


class PlanResponse(BaseModel):
    id: int
    name: str


class PlanResponseExtended(BaseModel):
    plan: str
    permission: str
