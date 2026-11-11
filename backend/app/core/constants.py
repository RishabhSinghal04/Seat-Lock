from datetime import timedelta
from typing import Final

MAX_EMAIL_LENGTH: Final[int] = 254
MAX_PASSWORD_LENGTH: Final[int] = 128
MAX_NAME_LENGTH: Final[int] = 128
MAX_ALLOWED_AGE: Final[int] = 100

MIN_EMAIL_LENGTH: Final[int] = 5
MIN_PASSWORD_LENGTH: Final[int] = 8
MIN_NAME_LENGTH: Final[int] = 2
MIN_ALLOWED_AGE: Final[int] = 18

MONEY_PRECISION: Final[int] = 10
MONEY_SCALE: Final[int] = 2
MAX_PAYMENT_REFERENCE_LENGTH: Final[int] = 255
MAX_CURRENCY_LENGTH: Final[int] = 3

CODE_DIGITS: Final[int] = 6
MAX_CODE_ATTEMPTS: Final[int] = 5
TOKEN_HASH_LENGTH: Final[int] = 64

CODE_TTL: Final[timedelta] = timedelta(minutes=10)
HOLD_DURATION: Final[timedelta] = timedelta(minutes=10)

MAX_EVENT_NAME_LENGTH: Final[int] = 256
MAX_ONLINE_URL_LENGTH: Final[int] = 500
MAX_SEAT_NUMBER_LENGTH: Final[int] = 20
MAX_CATEGORY_SLUG_LENGTH: Final[int] = 50
MAX_CATEGORY_NAME_LENGTH: Final[int] = 100

MAX_VENUE_LENGTH: Final[int] = 255
MAX_STREET_LENGTH: Final[int] = 255
MAX_LOCALITY_LENGTH: Final[int] = 100
MAX_CITY_LENGTH: Final[int] = 100
MAX_STATE_LENGTH: Final[int] = 100
MAX_POSTAL_CODE_LENGTH: Final[int] = 16
MAX_COUNTRY_CODE_LENGTH: Final[int] = 3
MAX_TIMEZONE_LENGTH: Final[int] = 50
