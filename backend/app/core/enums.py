from enum import StrEnum


class SMTPSecurity(StrEnum):
    STARTTLS = "starttls"
    TLS = "tls"
    PLAINTEXT = "plaintext"


class ReservationStatus(StrEnum):
    HELD = "held"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class EventStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class EventFormat(StrEnum):
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    HYBRID = "hybrid"


class RefundStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TokenClaims(StrEnum):
    JWT_ID = "jti"
    SUBJECT = "sub"
    TYPE = "type"
    ISSUED_AT = "iat"
    EXPIRY = "exp"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class AuthScheme(StrEnum):
    BEARER = "bearer"


class TokenPurpose(StrEnum):
    EMAIL_VERIFICATION = "email_verification"
    EMAIL_CHANGE = "email_change"
    PASSWORD_RESET = "password_reset"
