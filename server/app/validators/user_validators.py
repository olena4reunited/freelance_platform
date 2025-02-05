import re
from fastapi import HTTPException


def validate_email(email: str):
    email_regex = r"\w+@[a-zA-Z_]+\.[a-zA-Z]{2,6}"

    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email")


def validate_password(password):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit")
    if not re.search(r"[!-\/:-@[-`{-~]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")


def validate_phone_number(username):
    phone_number_regex = r"^\+?\d{10, 12}$"
    if not re.match(phone_number_regex, username):
        raise HTTPException(status_code=400, detail="Invalid phone number")
