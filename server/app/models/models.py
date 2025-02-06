from server.app.models._base_model import BaseModel


class Plan(BaseModel):
    table_name = "plans"


class Permission(BaseModel):
    table_name = "permissions"


class PlanPermission(BaseModel):
    table_name = "plans_permissions"


class User(BaseModel):
    table_name = "users"


class Payment(BaseModel):
    table_name = "payments"
