import re
from enum import Enum

from server.app.models.user_model import User
from server.app.utils.auth import verify_password
from server.app.utils.exceptions import CustomHTTPException


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
            CustomHTTPException.bad_request(detail="Could not process request: Username is required")
        if User.get_user_by_field("username", self.username):
            CustomHTTPException.bad_request(detail="Could not process request: This username is already taken")

        return self

    def validate_email(self):
        if not self.email and self.method:
            CustomHTTPException.bad_request(detail="Could not process request: Email is required")
        if not self.email and not self.method:
            return self
        if User.get_user_by_field("email", self.email):
            CustomHTTPException.bad_request(detail="Could not process request: This email is already registered")

        email_regex = r"^[a-zA-Z\d?+\.a-zA-Z\d?+]+@[a-zA-Z]+\.[a-zA-Z]{2,6}"

        if not re.match(email_regex, self.email):
            CustomHTTPException.bad_request(detail="Could not process request: Invalid email format")

        return self

    def validate_password(self):
        if not self.password and self.method:
            CustomHTTPException.bad_request(detail="Could not process request: Password is required")
        if not self.password and not self.method:
            return self
        if not (self.password == self.password_repeat):
            CustomHTTPException.bad_request(detail="Could not process request: Passwords do not match")

        if len(self.password) < 8:
            CustomHTTPException.bad_request(detail="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", self.password):
            CustomHTTPException.bad_request(detail="Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", self.password):
            CustomHTTPException.bad_request(detail="Password must contain at least one lowercase letter")
        if not re.search(r"\d", self.password):
            CustomHTTPException.bad_request(detail="Password must contain at least one digit")
        if not re.search(r"[!-/:-@[-`{-~]", self.password):
            CustomHTTPException.bad_request(detail="Password must contain at least one special character")

        return self

    def validate_phone_number(self):
        if not self.phone_number:
            return self
        if self.phone_number and User.get_user_by_field("phone_number", self.phone_number):
            CustomHTTPException.bad_request(detail="Could not process request: Phone number is already taken")

        phone_number_regex = r"^\+?\d{10,12}$"

        if not re.match(phone_number_regex, self.phone_number):
            CustomHTTPException.bad_request(detail="Could not process request: Invalid phone number")

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
            CustomHTTPException.not_found(detail="Could not process request: User does not exist")
        if not verify_password(self.password, user["password"]):
            CustomHTTPException.bad_request(detail="Could not process request: Password does not match")

        return self
