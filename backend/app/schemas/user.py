import uuid

from app.schemas.base import BaseResponse, BaseSchema
from app.schemas.types import (
    DOB,
    Email,
    LoginEmail,
    LoginPassword,
    Name,
    StrongPassword,
)


# -- Request --
class ProfileCreate(BaseSchema):
    name: Name
    dob: DOB


class ProfileUpdate(BaseSchema):
    name: Name | None = None
    dob: DOB | None = None


class EmailChange(BaseSchema):
    new_email: Email
    current_password: LoginPassword


class PasswordChange(BaseSchema):
    current_password: LoginPassword
    new_password: StrongPassword


# -- Response --
class UserResponse(BaseResponse):
    user_id: uuid.UUID
    email: LoginEmail
    name: Name | None = None
    dob: DOB | None = None
    is_active: bool
    is_verified: bool
