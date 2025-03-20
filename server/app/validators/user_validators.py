import re
from enum import Enum

from server.app.models.user_model import User
from server.app.utils.auth import verify_password
from server.app.utils.exceptions import GlobalException


class MethodEnum(Enum):
    create = 1
    update = 0


class UserValidator:
    def __init__(
            self,
            method: MethodEnum | None = None,
            username: str | None = None,
            email: str | None = None,
            password: str | None = None,
            password_repeat: str | None = None,
            phone_number: str | None = None
    ):
        self.method = method.value if method else None
        self.username = username
        self.email = email
        self.password = password
        self.password_repeat = password_repeat
        self.phone_number = phone_number

    def validate_username(self):
        if not self.username and self.method:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Username cannot be empty"
            )
        if User.get_user_by_field("username", self.username):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Username already exists. Username must be unique"
            )
        return self

    def validate_email(self):
        if not self.email and self.method:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Email cannot be empty"
            )
        if not self.email and not self.method:
            return self
        if User.get_user_by_field("email", self.email):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Email already registered"
            )

        email_regex = r"^[a-zA-Z\d?+\.a-zA-Z\d?+]+@[a-zA-Z]+\.[a-zA-Z]{2,6}"

        if not re.match(email_regex, self.email):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Could not process email address validation. Enter a valid email address"
            )

        return self

    def validate_password(self):
        if not self.password and self.method:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password is required"
            )
        if not self.password and not self.method:
            return self
        
        if self.password != self.password_repeat:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Passwords don't match"
            )
        if not self.password_repeat:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Repeat your password"
            )

        if len(self.password) < 8:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        if not re.search(r"[A-Z]", self.password):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password must contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", self.password):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password must contain at least one lowercase letter"
            )
        if not re.search(r"\d", self.password):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password must contain at least one digit"
            )
        if not re.search(r"[!-/:-@[-`{-~]", self.password):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password must contain at least one special character"
            )
        return self

    def validate_phone_number(self):
        if not self.phone_number:
            return self
        if self.phone_number and User.get_user_by_field("phone_number", self.phone_number):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Phone number already registered"
            )

        phone_number_regex = r"^\+?\d{10,12}$"

        if not re.match(phone_number_regex, self.phone_number):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Could not process phone number validation. Enter a valid phone number"
            )

        return self


class UserTokenValidator:
    def __init__(
            self,
            password: str,
            email : str | None = None,
            username : str | None = None
    ):
        self.password = password
        self.email = email
        self.username = username

    def validate_user_exists(self):
        user = dict()

        if self.username:
            user = User.get_user_by_field("username", self.username)
        if self.email:
            user = User.get_user_by_field("email", self.email)

        if not user:
            GlobalException.CustomHTTPException.raise_exception(
                status_code=404,
                detail="User does not exist",
                extra={"username": self.username, "email": self.email}
            )
        if not verify_password(self.password, user["password"]):
            GlobalException.CustomHTTPException.raise_exception(
                status_code=400,
                detail="Password does not match"
            )

        return self
