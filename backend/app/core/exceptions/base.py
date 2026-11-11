from http import HTTPStatus
from typing import override

type JSONValue = (
    str | int | float | bool | None | list[JSONValue] | dict[str, JSONValue]
)


class AppError(Exception):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_message = "an unexpected error occurred"
    extra: dict[str, JSONValue] | None = None

    def __init__(
        self, message: str | None = None, extra: dict[str, JSONValue] | None = None
    ) -> None:
        self.message: str = message if message is not None else self.default_message
        self.extra = extra or {}
        super().__init__(self.message)

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code.value}, message={self.message!r}, extra={self.extra!r})"


class BadRequestError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    default_message = "The request could not be processed due to invalid input."


class AuthenticationError(AppError):
    status_code = HTTPStatus.UNAUTHORIZED
    default_message = "Authentication failed. Credentials are missing or invalid."


class AuthorizationError(AppError):
    status_code = HTTPStatus.FORBIDDEN
    default_message = "You do not have permission to access this resource."


class NotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    default_message = "The requested resource was not found"


class MethodNotAllowed(AppError):
    status_code = HTTPStatus.METHOD_NOT_ALLOWED
    default_message = "This HTTP method is not allowed for the requested resource."


class RequestTimeout(AppError):
    status_code = HTTPStatus.REQUEST_TIMEOUT
    default_message = "The request timed out. Please try again."


class ConflictError(AppError):
    status_code = HTTPStatus.CONFLICT
    default_message = "The request conflicts with the current state of the resource."


class TooManyRequestsError(AppError):
    status_code = HTTPStatus.TOO_MANY_REQUESTS
    default_message = "Too many requests. Please try again later."
