from datetime import timedelta
from typing import Final

MAX_EMAIL_LENGTH: Final[int] = 254

MONEY_PRECISION: Final[int] = 10
MONEY_SCALE: Final[int] = 2
MAX_PAYMENT_REFERENCE_LENGTH: Final[int] = 255
MAX_CURRENCY_LENGTH: Final[int] = 3

HOLD_DURATION: Final[timedelta] = timedelta(minutes=10)

MAX_EVENT_NAME_LENGTH: Final[int] = 256
MAX_ONLINE_URL_LENGTH: Final[int] = 500
MAX_SEAT_NUMBER_LENGTH: Final[int] = 20
MAX_CATEGORY_SLUG_LENGTH: Final[int] = 50
MAX_CATEGORY_NAME_LENGTH: Final[int] = 100

# Venue related constants
MAX_VENUE_LENGTH: Final[int] = 255
MAX_STREET_LENGTH: Final[int] = 255
MAX_LOCALITY_LENGTH: Final[int] = 100
MAX_CITY_LENGTH: Final[int] = 100
MAX_STATE_LENGTH: Final[int] = 100
MAX_POSTAL_CODE_LENGTH: Final[int] = 16
MAX_COUNTRY_CODE_LENGTH: Final[int] = 3
MAX_TIMEZONE_LENGTH: Final[int] = 50
