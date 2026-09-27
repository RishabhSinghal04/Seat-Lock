import os
from typing import Final, Self

from dotenv import load_dotenv
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

"""ACCESS_TOKEN_TIMEOUT in minutes and REFRESH_TOKEN_TIMEOUT in days"""

_ALLOWED_ALGORITHMS: frozenset[str] = frozenset({"HS256", "HS384", "HS512"})
_DEFAULT_ALGORITHM: Final[str] = "HS256"
_DEFAULT_ACCESS_TOKEN_TIMEOUT: Final[int] = 30
_DEFAULT_REFRESH_TOKEN_TIMEOUT: Final[int] = 7
_SHARED_SETTINGS = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")


def _ensure_positive(value: int) -> int:
    if value <= 0:
        raise ValueError("must be greater than 0")
    return value


class AuthConfig(BaseSettings):
    model_config = _SHARED_SETTINGS

    KEY: SecretStr
    ALGORITHM: str
    ACCESS_TOKEN_TIMEOUT: int
    REFRESH_TOKEN_TIMEOUT: int

    @field_validator("ALGORITHM")
    @classmethod
    def _validate_algorithm(cls, algorithm: str) -> str:
        if algorithm not in _ALLOWED_ALGORITHMS:
            raise ValueError(f"unsupported algorithm: {algorithm}")
        return algorithm

    @field_validator("ACCESS_TOKEN_TIMEOUT", "REFRESH_TOKEN_TIMEOUT")
    @classmethod
    def _ensure_positive_timeout(cls, value: int) -> int:
        return _ensure_positive(value)


class DatabaseConfig(BaseSettings):
    model_config = _SHARED_SETTINGS

    DATABASE_URL: str


class Config(AuthConfig, DatabaseConfig):
    DEBUG: bool = False
    TESTING: bool = False
    ALLOWED_ORIGIN: str


class DevelopmentConfig(Config):
    KEY: SecretStr = SecretStr("dev-key-minimum-32-characters-long")
    ALGORITHM: str = _DEFAULT_ALGORITHM
    ACCESS_TOKEN_TIMEOUT: int = _DEFAULT_ACCESS_TOKEN_TIMEOUT
    REFRESH_TOKEN_TIMEOUT: int = _DEFAULT_REFRESH_TOKEN_TIMEOUT
    DATABASE_URL: str = Field(..., validation_alias="DEV_DATABASE_URL")
    DEBUG: bool = True


class ConfigTest(Config):
    KEY: SecretStr = SecretStr("test-key-minimum-32-characters-long")
    ALGORITHM: str = _DEFAULT_ALGORITHM
    ACCESS_TOKEN_TIMEOUT: int = _DEFAULT_ACCESS_TOKEN_TIMEOUT
    REFRESH_TOKEN_TIMEOUT: int = _DEFAULT_REFRESH_TOKEN_TIMEOUT
    DATABASE_URL: str = Field(..., validation_alias="TEST_DATABASE_URL")
    TESTING: bool = True


class ProductionConfig(Config):
    KEY: SecretStr = Field(...)
    ALGORITHM: str = Field(default=_DEFAULT_ALGORITHM)
    ACCESS_TOKEN_TIMEOUT: int = Field(default=_DEFAULT_ACCESS_TOKEN_TIMEOUT)
    REFRESH_TOKEN_TIMEOUT: int = Field(default=_DEFAULT_REFRESH_TOKEN_TIMEOUT)
    ALLOWED_ORIGIN: str = Field(...)
    DATABASE_URL: str

    @model_validator(mode="after")
    def _check_required(self) -> Self:
        if not self.KEY.get_secret_value().strip():
            raise ValueError("KEY cannot be empty")
        if not self.ALLOWED_ORIGIN.strip():
            raise ValueError("ALLOWED_ORIGIN cannot be empty")
        return self


_config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": ConfigTest,
    "production": ProductionConfig,
}


def get_config() -> Config:
    env: str = os.environ.get("ENVIRONMENT", "development")
    if env not in _config:
        raise SystemExit(
            f"[config] ENVIRONMENT must be in {list(_config.keys())}, got '{env}'"
        )
    cls: type[Config] = _config[env]
    return cls()
    # return cls.model_validate({})
