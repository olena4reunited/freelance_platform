from typing import Any, Union

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from fastapi.requests import Request

from server.app.schemas.token_schemas import Token
from server.app.schemas.users_schemas import (
    UserResponse,
    UserResponsePerformer,
    UserResponseExtended,
    UserResponseExtendedPerformer,
    UserCreateCustomer,
    UserCreatePerformer,
    UserCreateToken,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from server.app.controllers.user_controller import UserController
from server.app.validators.user_validators import (
    UserValidator,
    UserTokenValidator,
    MethodEnum
)
from server.app.utils.dependencies.dependencies import (
    get_current_user,
    required_plans,
    required_permissions
)
from server.app.utils.exceptions import GlobalException
from server.app.utils.auth import oauth
from server.app.services.smtp_service import send_reset_code


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/google/login")
async def google_login(
    request: Request,
    plan: str = Query(None, regex="^(customer|performer)$")
):
    request.session["plan"] = plan
    return await oauth.google.authorize_redirect(
        request, 
        request.url_for("google_callback")
    )


@router.get("/google/callback", response_model=Token)
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    plan = request.session.pop("plan", None)

    return await UserController.authenticate_user_google(token=token, plan=plan)


@router.post("/customer/register", response_model=UserResponse)
@GlobalException.catcher
def create_user_customer(user_customer_data: UserCreateCustomer):
    UserValidator(
            MethodEnum.create,
            user_customer_data.username,
            user_customer_data.email,
            user_customer_data.password,
            user_customer_data.password_repeat,
            user_customer_data.phone_number) \
            .validate_username() \
            .validate_email() \
            .validate_password() \
            .validate_phone_number()

    return UserController.create_user_customer(user_customer_data.model_dump())


@router.post("/performer/register", response_model=UserResponsePerformer)
@GlobalException.catcher
def create_user_performer(user_performer_data: UserCreatePerformer):
    UserValidator(
        MethodEnum.create,
        user_performer_data.username,
        user_performer_data.email,
        user_performer_data.password,
        user_performer_data.password_repeat,
        user_performer_data.phone_number) \
        .validate_username() \
        .validate_email() \
        .validate_password() \
        .validate_phone_number()

    return UserController.create_user_performer(user_performer_data.model_dump())


@router.post("/token", response_model=Token)
@GlobalException.catcher
def create_user_token(user_data: UserCreateToken):
    UserTokenValidator(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password) \
    .validate_user_exists()

    return UserController.authenticate_user(user_data.model_dump())


@router.post("/token/refresh", response_model=Token)
@GlobalException.catcher
def refresh_user_token(refresh_tkn: dict[str, str]):
    return UserController.refresh_bearer_token(refresh_tkn["refresh_token"])


@router.get("/me", response_model=Union[UserResponse, UserResponsePerformer])
@GlobalException.catcher
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_own_user_details"])
def read_user_me(user: dict[str, Any] = Depends(get_current_user)):
    if user.get("plan_name") == "performer":
        UserController.add_performer_specialities(user)
    
    return user


@router.post("/password/reset")
@GlobalException.catcher
def reset_password(data: PasswordResetRequest):
    email = data.email
    code = UserController.password_reset_request(email)
    
    send_reset_code(email, code)


@router.post("/password/reset/confirm")
@GlobalException.catcher
def confirm_reset_password(data: PasswordResetConfirmRequest):
    return UserController.password_reset_confirm_request(data.model_dump())


@router.patch("/me", response_model=Union[UserResponse, UserResponsePerformer])
@GlobalException.catcher
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_own_user_details", "update_own_user_details"])
def update_user(
        updated_user_data: dict[str, Any],
        user: dict[str, Any] = Depends(get_current_user)
):
    UserValidator(
        MethodEnum.update,
        updated_user_data.get("username", None),
        updated_user_data.get("email", None),
        updated_user_data.get("password", None),
        updated_user_data.get("password_repeat", None),
        updated_user_data.get("phone_number", None)) \
        .validate_username() \
        .validate_email() \
        .validate_password() \
        .validate_phone_number()

    user = UserController.update_user(user["id"], updated_user_data)

    if user.get("plan_name") == "performer":
        UserController.add_performer_specialities(user)
    
    return user


@router.delete("/me", status_code=204)
@GlobalException.catcher
@required_plans(["admin", "moderator", "customer", "performer"])
@required_permissions(["read_own_user_details", "update_own_user_details", "delete_own_user"])
def delete_user(
        user: dict[str, Any] = Depends(get_current_user)
):
    UserController.delete_user(user["id"])

    return


@router.get("/list", response_model=list[UserResponse])
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_list"])
def read_all_users(
        plan: str = Query(None, description="filter by role"),
        limit: int = Query(None, description="number of users to return"),
        user: dict[str, Any] = Depends(get_current_user)
):
    return UserController.get_all_users(plan, limit)


@router.get("/{user_id}", response_model=Union[UserResponseExtended, UserResponseExtendedPerformer])
@GlobalException.catcher
@required_plans(["admin", "moderator"])
@required_permissions(["read_all_users_list", "read_user_details"])
def get_user(
        user_id: int,
        user: dict[str, Any] = Depends(get_current_user)
):
    user = UserController.get_user(user_id)
    
    if user.get("plan_name") == "performer":
        UserController.add_performer_specialities(user)
    
    return user


@router.patch("/{user_id}", response_model=Union[UserResponseExtended, UserResponseExtendedPerformer])
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_all_users_list", "read_user_details", "update_user_details"])
def edit_user(
        user_id: int,
        updated_user_data: dict[str, Any],
        user : dict[str, Any] = Depends(get_current_user)
):
    UserValidator(
        MethodEnum.update,
        updated_user_data.get("username", None),
        updated_user_data.get("email", None),
        updated_user_data.get("password", None),
        updated_user_data.get("password_repeat", None),
        updated_user_data.get("phone_number", None)) \
        .validate_username() \
        .validate_email() \
        .validate_password() \
        .validate_phone_number()

    user = UserController.update_user_details(user_id, updated_user_data)

    if user.get("plan_name") == "performer":
        UserController.add_performer_specialities(user)

    return user


@router.delete("/{user_id}", status_code=204)
@GlobalException.catcher
@required_plans(["admin"])
@required_permissions(["read_user_details", "update_user_details", "delete_user"])
def delete_user(
        user_id: int,
        user : dict[str, Any] = Depends(get_current_user)
):
    UserController.delete_user(user_id)

    return
