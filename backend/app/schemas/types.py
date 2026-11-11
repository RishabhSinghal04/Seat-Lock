import re
from datetime import date
from typing import Annotated

from disposable_email_domains import blocklist
from pydantic import AfterValidator, EmailStr, Field, SecretStr, StringConstraints

from app.core.constants import (
    MAX_ALLOWED_AGE,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_ALLOWED_AGE,
    MIN_EMAIL_LENGTH,
    MIN_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
)

PASSWORD_VALIDATION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[a-z]"), "password must contain at least one lowercase letter"),
    (re.compile(r"[A-Z]"), "password must contain at least one uppercase letter"),
    (re.compile(r"[0-9]"), "password must contain at least one digit"),
    (
        re.compile(r"[^A-Za-z0-9]"),
        "password must contain at least one special character",
    ),
)


def _reject_disposable_email(email: str) -> str:
    domain_parts: list[str] = email.rsplit("@", 1)[1].split(".")
    if any(
        ".".join(domain_parts[i:]) in blocklist for i in range(len(domain_parts) - 1)
    ):
        raise ValueError("disposable email addresses are not allowed")
    return email


def _check_password_strength(password: SecretStr) -> SecretStr:
    value: str = password.get_secret_value()
    validation_rules: tuple[tuple[re.Pattern[str], str], ...] = (
        PASSWORD_VALIDATION_RULES
    )
    for pattern, error in validation_rules:
        if not pattern.search(value):
            raise ValueError(error)
    return password


def _normalize_name(name: str) -> str:
    return " ".join(name.split())


def _check_dob(dob: date) -> date:
    today: date = date.today()
    if dob > today:
        raise ValueError("date of birth cannot be in future")
    current_age: int = (
        today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    )
    if not MIN_ALLOWED_AGE <= current_age <= MAX_ALLOWED_AGE:
        raise ValueError(
            f"age must be between {MIN_ALLOWED_AGE} and {MAX_ALLOWED_AGE} years"
        )
    return dob


LoginEmail = Annotated[
    EmailStr, Field(max_length=MAX_EMAIL_LENGTH), AfterValidator(str.lower)
]
LoginPassword = Annotated[SecretStr, Field(max_length=MAX_PASSWORD_LENGTH)]

Email = Annotated[
    LoginEmail,
    Field(min_length=MIN_EMAIL_LENGTH),
    AfterValidator(_reject_disposable_email),
]
StrongPassword = Annotated[
    LoginPassword,
    Field(min_length=MIN_PASSWORD_LENGTH),
    AfterValidator(_check_password_strength),
]

Name = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH
    ),
    AfterValidator(_normalize_name),
]
DOB = Annotated[date, AfterValidator(_check_dob)]
