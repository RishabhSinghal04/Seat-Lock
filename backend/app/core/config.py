from functools import cache
from pathlib import Path
from typing import Annotated, Final, Literal, Self

from pydantic import (
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import SMTPSecurity

Environment = Literal["development", "testing", "production"]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

_MIN_JWT_KEY_BYTES: Final[dict[str, int]] = {"HS256": 32, "HS384": 48, "HS512": 64}
_ENV_FILE: Final[Path] = Path(__file__).resolve().parents[2] / ".env"
_ENV_FILE_TEST: Final[Path] = Path(__file__).resolve().parents[2] / ".env.testing"


class _BaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore", frozen=True
    )


class AuthConfig(_BaseSettings):
    JWT_KEY: SecretStr
    ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, gt=0, description="Access token lifetime in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, gt=0, description="Refresh token lifetime in days"
    )

    @model_validator(mode="after")
    def _check_jwt_key_length(self) -> Self:
        required: int = _MIN_JWT_KEY_BYTES[self.ALGORITHM]
        if len(self.JWT_KEY.get_secret_value().encode()) < required:
            raise ValueError(
                f"JWT_KEY must be at least {required} bytes for {self.ALGORITHM}"
            )
        return self


class DatabaseConfig(_BaseSettings):
    DATABASE_URL: SecretStr


class SMTPConfig(_BaseSettings):
    SMTP_HOST: NonEmptyStr
    SMTP_PORT: int = Field(gt=0, le=65535)
    SMTP_USER: str = ""
    SMTP_PASSWORD: SecretStr = SecretStr("")
    SMTP_SECURITY: SMTPSecurity
    SMTP_TIMEOUT_SECONDS: float = Field(gt=0, le=30)
    EMAIL_FROM_ADDRESS: EmailStr
    EMAIL_FROM_NAME: NonEmptyStr

    @property
    def use_tls(self) -> bool:
        return self.SMTP_SECURITY is SMTPSecurity.TLS

    @property
    def start_tls(self) -> bool:
        return self.SMTP_SECURITY is SMTPSecurity.STARTTLS

    @model_validator(mode="after")
    def _check_credentials(self) -> Self:
        has_user = bool(self.SMTP_USER)
        has_password = bool(self.SMTP_PASSWORD.get_secret_value())
        if has_user != has_password:
            raise ValueError("SMTP_USER and SMTP_PASSWORD must be set together")
        if has_user and self.SMTP_SECURITY is SMTPSecurity.PLAINTEXT:
            raise ValueError("SMTP credentials must not be set without TLS")
        return self


class Config(AuthConfig, DatabaseConfig, SMTPConfig):
    DEBUG: bool = False
    TESTING: bool = False
    ALLOWED_ORIGIN: NonEmptyStr


class DevelopmentConfig(Config):
    JWT_KEY: SecretStr = SecretStr("dev-jwt-key-minimum-32-characters-long")
    DATABASE_URL: SecretStr = Field(..., validation_alias="DEV_DATABASE_URL")
    DEBUG: bool = True


class ConfigTest(Config):
    model_config = SettingsConfigDict(env_file=_ENV_FILE_TEST)
    JWT_KEY: SecretStr = SecretStr("test-jwt-key-minimum-32-characters-long")
    DATABASE_URL: SecretStr = Field(..., validation_alias="TEST_DATABASE_URL")
    TESTING: bool = True


class ProductionConfig(Config):
    @model_validator(mode="after")
    def _check_production_safety(self) -> Self:
        if self.DEBUG or self.TESTING:
            raise ValueError("DEBUG or TESTING must be false in production")
        if self.SMTP_SECURITY is SMTPSecurity.PLAINTEXT:
            raise ValueError(
                f"SMTP_SECURITY must not be {SMTPSecurity.PLAINTEXT.value!r} in production"
            )
        return self

    @field_validator("ALLOWED_ORIGIN")
    @classmethod
    def _reject_wildcard_origin(cls, origin: str) -> str:
        if origin == "*":
            raise ValueError("wildcard origin is not allowed in production")
        return origin


class _Bootstrap(_BaseSettings):
    ENVIRONMENT: Environment = "production"


_CONFIGS: Final[dict[Environment, type[Config]]] = {
    "development": DevelopmentConfig,
    "testing": ConfigTest,
    "production": ProductionConfig,
}


@cache
def get_config() -> Config:
    return _CONFIGS[_Bootstrap().ENVIRONMENT]()
