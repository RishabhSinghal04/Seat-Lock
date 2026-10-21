from datetime import timedelta
from typing import Final

# User related constants
MAX_EMAIL_LENGTH: Final[int] = 254

# Money related constants
MONEY_PRECISION: Final[int] = 10
MONEY_SCALE: Final[int] = 2
MAX_PAYMENT_REFERENCE_LENGTH: Final[int] = 255

# Time related constants
HOLD_DURATION: Final[timedelta] = timedelta(minutes=10)

# Event related constants
MAX_EVENT_NAME_LENGTH: Final[int] = 256

# Venue related constants
MAX_VENUE_LENGTH: Final[int] = 255
MAX_STREET_LENGTH: Final[int] = 255
MAX_LOCALITY_LENGTH: Final[int] = 100
MAX_CITY_LENGTH: Final[int] = 100
MAX_STATE_LENGTH: Final[int] = 100
MAX_POSTAL_CODE_LENGTH: Final[int] = 16
MAX_COUNTRY_CODE_LENGTH: Final[int] = 3
MAX_TIMEZONE_LENGTH: Final[int] = 50
