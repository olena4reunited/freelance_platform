import re
from enum import Enum

from fastapi import HTTPException
from starlette import status

from server.app.models.user_model import User
from server.app.utils.auth import verify_password


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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")
        if User.get_user_by_field("username", self.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username is already registered")

        return self

    def validate_email(self):
        if not self.email and self.method:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
        if not self.email and not self.method:
            return self
        if User.get_user_by_field("email", self.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

        email_regex = r"^[a-zA-Z_\.a-zA-Z]+@[a-zA-Z_]+\.[a-zA-Z]{2,6}"

        if not re.match(email_regex, self.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")

        return self

    def validate_password(self):
        if not self.password and self.method:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")
        if not self.password and not self.method:
            return self
        if not (self.password == self.password_repeat):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords don't match")

        if len(self.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", self.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", self.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter")
        if not re.search(r"\d", self.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one digit")
        if not re.search(r"[!-/:-@[-`{-~]", self.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one special character")

        return self

    def validate_phone_number(self):
        if not self.phone_number:
            return self
        if self.phone_number and User.get_user_by_field("phone_number", self.phone_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is already registered")


        phone_number_regex = r"^\+?\d{10,12}$"

        if not re.match(phone_number_regex, self.phone_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number")

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not verify_password(self.password, user["password"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

        return self
