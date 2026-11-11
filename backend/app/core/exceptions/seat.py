import uuid

from app.core.exceptions.base import ConflictError


class SeatUnavailableError(ConflictError):
    default_message = "The selected seat is no longer available."

    def __init__(self, seat_id: uuid.UUID) -> None:
        super().__init__(extra={"seat_id": str(seat_id)})
