from enum import StrEnum


class ReservationStatus(StrEnum):
    CONFIRMED = "confirmed"
    HELD = "held"


class EventStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
