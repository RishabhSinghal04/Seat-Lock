from datetime import timedelta
from typing import Final

MAX_EMAIL_LENGTH: Final[int] = 254
MAX_EVENT_NAME_LENGTH: Final[int] = 256
MAX_VENUE_LENGTH: Final[int] = 256
MAX_PAYMENT_REFERENCE_LENGTH: Final[int] = 255
MONEY_PRECISION: Final[int] = 10
MONEY_SCALE: Final[int] = 2
HOLD_DURATION: Final[timedelta] = timedelta(minutes=10)
