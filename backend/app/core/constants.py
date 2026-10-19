from datetime import timedelta
from enum import StrEnum
from typing import Final

MAX_EMAIL_LENGTH: Final[int] = 254
MAX_EVENT_NAME_LENGTH: Final[int] = 256
MAX_VENUE_LENGTH: Final[int] = 256
MAX_PAYMENT_REFERENCE_LENGTH: Final[int] = 255
MAX_INTEGER_DIGITS: Final[int] = 10
DECIMAL_PLACES: Final[int] = 2
HOLD_DURATION_INTERVAL: Final[timedelta] = timedelta(minutes=10)


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    HELD = "held"
    BOOKED = "booked"
