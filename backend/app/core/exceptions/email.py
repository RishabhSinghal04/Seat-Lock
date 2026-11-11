from http import HTTPStatus

from app.core.exceptions.base import AppError


class EmailDeliveryError(AppError):
    status_code = HTTPStatus.BAD_GATEWAY
    default_message = "The email could not be delivered. Please try again."
