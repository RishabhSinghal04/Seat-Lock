from app.core.exceptions.base import AuthenticationError, ConflictError


class InvalidCredentialsError(AuthenticationError):
    default_message = "Invalid email or password"


class InvalidCodeError(AuthenticationError):
    default_message = "Invalid or expired verification code"


class ResourceInUseError(ConflictError):
    default_message = (
        "This record cannot be deleted because other records still reference it."
    )
