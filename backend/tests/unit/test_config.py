import re
from collections.abc import Callable
from typing import Final, Literal

import pytest
from _pytest.raises import RaisesExc
from app.core import Config
from app.core.config import AuthConfig, ConfigTest, DevelopmentConfig, ProductionConfig
from pydantic import ValidationError
from pytest import MonkeyPatch

type EnvOverrides = dict[str, str]
type SetEnv = Callable[..., None]

COMMON_ENV: Final[EnvOverrides] = {
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "your-email@gmail.com",
    "SMTP_PASSWORD": "app-password",
    "SMTP_SECURITY": "starttls",
    "SMTP_TIMEOUT_SECONDS": "10",
    "EMAIL_FROM_ADDRESS": "your-email@gmail.com",
    "EMAIL_FROM_NAME": "SeatLock",
    "DATABASE_URL": "postgresql+asyncpg://username:password@localhost:5432/test_database",
    "JWT_KEY": "your-minimum-32-character-jwt-key-here",
    "ALGORITHM": "HS256",
    "ALLOWED_ORIGIN": "https://localhost:0000",
}

ALL_CONFIGS: Final = (ProductionConfig, DevelopmentConfig, ConfigTest)

EXTRA_ENV_NAMES: Final = {
    "ENVIRONMENT",
    "DEBUG",
    "TESTING",
    "DEV_DATABASE_URL",
    "TEST_DATABASE_URL",
}


# -- Fixtures and helpers --
@pytest.fixture(autouse=True)
def clean_env(monkeypatch: MonkeyPatch) -> None:
    """Remove real config env vars so tests only see what they set."""
    names: set[str] = {
        name for cls in (Config, *ALL_CONFIGS) for name in cls.model_fields
    }
    for name in names | EXTRA_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def set_env(monkeypatch: MonkeyPatch) -> SetEnv:
    """Return a function that applies COMMON_ENV plus overrides, minus remove."""

    def _set_env(
        overrides: EnvOverrides | None = None, remove: tuple[str, ...] = ()
    ) -> None:
        env: EnvOverrides = {**COMMON_ENV, **(overrides or {})}
        for key in remove:
            env.pop(key, None)
        for key, value in env.items():
            monkeypatch.setenv(key, value)

    return _set_env


def load_production() -> ProductionConfig:
    """Instantiate ProductionConfig from the environment only (ignore .env)."""
    return ProductionConfig(_env_file=None)


def expect_rejection[E: BaseException](
    message: str | None = None, exc_type: type[E] = ValidationError
) -> RaisesExc[E]:
    """pytest.raises for a validation failure whose message contains 'message'."""
    return pytest.raises(exc_type, match=re.escape(message) if message else None)


def assert_field_error(
    exc_info: pytest.ExceptionInfo[ValidationError],
    field: str,
    error_type: str | None = None,
) -> None:
    """Assert validation failed on `field` (optionally with a given error type)."""
    assert any(
        error["loc"] == (field,) and (error_type is None or error["type"] == error_type)
        for error in exc_info.value.errors()
    ), f"No {error_type or 'validation'} error for {field!r}: {exc_info.value}"


# -- AuthConfig --
@pytest.mark.parametrize(
    ("jwt_key", "algorithm", "message"),
    [
        pytest.param(
            "too short", "HS256", "JWT_KEY must be at least 32 bytes", id="algo_hs256"
        ),
        pytest.param(
            "a" * 31, "HS384", "JWT_KEY must be at least 48 bytes", id="algo_hs384"
        ),
        pytest.param(
            "a" * 63, "HS512", "JWT_KEY must be at least 64 bytes", id="algo_512"
        ),
    ],
)
def test_jwt_key_too_short(
    jwt_key: str, algorithm: Literal["HS256", "HS384", "HS512"], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        AuthConfig(JWT_KEY=jwt_key, ALGORITHM=algorithm)


# -- Production only rules --
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"DEBUG": "True", "Testing": "False"}, id="debug_only"),
        pytest.param({"debug": "False", "TESTING": "True"}, id="testing_only"),
        pytest.param({"DEBUG": "True", "Testing": "True"}, id="both"),
    ],
)
def test_production_forbids_debug_or_testing(
    set_env: SetEnv, overrides: EnvOverrides
) -> None:
    set_env(overrides)
    with expect_rejection("DEBUG or TESTING must be false in production"):
        load_production()


def test_production_forbids_wildcard_origin(set_env: SetEnv) -> None:
    set_env({"ALLOWED_ORIGIN": "*"})
    with expect_rejection("Wildcard origin is not allowed in production", ValueError):
        load_production()


def test_production_forbids_plaintext_smtp(set_env: SetEnv) -> None:
    set_env({"SMTP_SECURITY": "plaintext"}, remove=("SMTP_USER", "SMTP_PASSWORD"))
    with expect_rejection(
        "SMTP_SECURITY must not be 'plaintext' in production", ValueError
    ):
        load_production()


# -- SMTP Credentials --
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param(
            {"SMTP_USER": "user@example.com", "SMTP_PASSWORD": ""}, id="no_password"
        ),
        pytest.param(
            {"SMTP_USER": "", "SMTP_PASSWORD": "SamplePassword"}, id="no_user"
        ),
    ],
)
def test_smtp_credentials_must_be_set_together(
    set_env: SetEnv, overrides: EnvOverrides
) -> None:
    set_env(overrides)
    with expect_rejection(
        "SMTP_USER and SMTP_PASSWORD must be set together", ValueError
    ):
        load_production()


def test_smtp_credentials_forbidden_without_tls(set_env: SetEnv) -> None:
    set_env(
        {
            "SMTP_SECURITY": "plaintext",
            "SMTP_USER": "admin",
            "SMTP_PASSWORD": "password",
        },
    )
    with expect_rejection("SMTP credentials must not be set without TLS", ValueError):
        load_production()


# -- Field level validation --
def test_misspelled_env_field(set_env: SetEnv) -> None:
    set_env({"SMTP_HOSTED": "smtp.gmail.com"}, remove=("SMTP_HOST",))
    with expect_rejection("") as exc_info:
        load_production()
    assert_field_error(exc_info, "SMTP_HOST", "missing")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        *[pytest.param("SMTP_PORT", v, id=f"port_{v}") for v in ["0", "-1", "65536"]],
        *[
            pytest.param("SMTP_TIMEOUT_SECONDS", v, id=f"timeout_{v}")
            for v in ["0", "-1", "30.1"]
        ],
        pytest.param("EMAIL_FROM_ADDRESS", "not-an-email", id="email_format"),
        *[
            pytest.param("EMAIL_FROM_NAME", v, id=f"from_name_{v!r}")
            for v in ["", "  "]
        ],
    ],
)
def test_invalid_field_value_rejected(set_env: SetEnv, field: str, value: str) -> None:
    set_env({field: value})
    with expect_rejection("") as exc_info:
        load_production()
    assert_field_error(exc_info, field)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        *[pytest.param("SMTP_PORT", v, id=f"port_{v}") for v in ["1", "65535"]],
        *[
            pytest.param("SMTP_TIMEOUT_SECONDS", v, id=f"timeout_{v}")
            for v in ["0.1", "30"]
        ],
    ],
)
def test_boundary_values_accepted(set_env: SetEnv, field: str, value: str) -> None:
    set_env({field: value})
    load_production()


@pytest.mark.parametrize("config_cls", ALL_CONFIGS, ids=lambda c: c.__name__)
@pytest.mark.parametrize("field", ["ACCESS_TOKEN_EXPIRE_MINUTES", "REFRESH_TOKEN_EXPIRE_DAYS"])
@pytest.mark.parametrize("value", ["0", "-1", ""])
def test_tokens(
    set_env: SetEnv, config_cls: type[Config], field: str, value: str
) -> None:
    set_env({field: value})
    with expect_rejection("", ValidationError) as exc_info:
        config_cls(_env_file=None)
    assert_field_error(exc_info, field)
