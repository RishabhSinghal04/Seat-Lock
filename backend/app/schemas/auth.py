from app.schemas.base import BaseSchema
from app.schemas.types import Email, LoginEmail, LoginPassword, StrongPassword


# -- Requests --
class UserSignup(BaseSchema):
    email: Email
    password: StrongPassword


class UserLogin(BaseSchema):
    email: LoginEmail
    password: LoginPassword


class PasswordForgot(BaseSchema):
    email: LoginEmail


class PasswordReset(BaseSchema):
    new_password: StrongPassword
