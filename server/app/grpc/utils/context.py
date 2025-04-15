from contextvars import ContextVar
from typing import TypeAlias


UserId: TypeAlias = int
UserUsername: TypeAlias = str
UserPlan: TypeAlias = str


user_id_var: ContextVar[UserId | None] = ContextVar("user_id", default=None)
user_username_var: ContextVar[UserUsername | None] = ContextVar("user_username", default=None)
user_plan_var: ContextVar[UserPlan | None] = ContextVar("user_plan", default=None)
