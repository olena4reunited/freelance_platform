import re
from enum import Enum

from fastapi import HTTPException


class MethodEnum(Enum):
    create = 1
    update = 0


class UserValidator:
    def __init__(
            self,
            method: MethodEnum,
            email: str | None = None,
            password: str | None = None,
            password_repeat: str | None = None,
            phone_number: str | None = None
    ):
        self.method = method.value
        self.email = email
        self.password = password
        self.password_repeat = password_repeat
        self.phone_number = phone_number


    def validate_email(self):
        if not self.email and self.method:
            raise HTTPException(status_code=400, detail="Email is required")
        if not self.email and not self.method:
            return self

        email_regex = r"\w+@[a-zA-Z_]+\.[a-zA-Z]{2,6}"

        if not re.match(email_regex, self.email):
            raise HTTPException(status_code=400, detail="Invalid email")

        return self


    def validate_password(self):
        if not self.password and self.method:
            raise HTTPException(status_code=400, detail="Password is required")
        if not self.password and not self.method:
            return self
        if not (self.password == self.password_repeat):
            raise HTTPException(status_code=400, detail="Passwords don't match")

        if len(self.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", self.password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", self.password):
            raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
        if not re.search(r"\d", self.password):
            raise HTTPException(status_code=400, detail="Password must contain at least one digit")
        if not re.search(r"[!-/:-@[-`{-~]", self.password):
            raise HTTPException(status_code=400, detail="Password must contain at least one special character")

        return self


    def validate_phone_number(self):
        if not self.phone_number:
            return self

        phone_number_regex = r"^\+?\d{10, 12}$"

        if not re.match(phone_number_regex, self.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number")

        return self
