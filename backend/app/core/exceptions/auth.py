from app.core.exceptions.base import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
)


class TokenExpiredError(AuthenticationError):
    default_message = "The authentication token has expired."


class InvalidTokenError(AuthenticationError):
    default_message = "The authentication token is invalid."


class UserNotVerifiedError(AuthorizationError):
    default_message = "Please verify your account before logging in."


class UserAlreadyExistsError(ConflictError):
    default_message = "A user with these details already exists."
