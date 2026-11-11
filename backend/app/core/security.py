import asyncio
import hashlib
import hmac
import logging
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from pydantic import SecretStr

from app.core.constants import CODE_DIGITS

logger: logging.Logger = logging.getLogger(__name__)
_hasher = PasswordHasher()

DUMMY_HASH: str = _hasher.hash(secrets.token_urlsafe(16))


async def hash_password(password: SecretStr) -> str:
    return await asyncio.to_thread(_hasher.hash, password.get_secret_value())


async def verify_password(hashed: str, password: SecretStr) -> bool:
    return await asyncio.to_thread(
        _verify_password, hashed, password.get_secret_value()
    )


def _verify_password(hashed: str, password: str) -> bool:
    try:
        return _hasher.verify(hash=hashed, password=password)
    except VerifyMismatchError:
        return False
    except (VerificationError, InvalidHashError):
        logger.exception("password verification failed")
        raise


def generate_numeric_code(digits: int = CODE_DIGITS) -> str:
    return f"{secrets.randbelow(10**digits):0{digits}d}"


def hash_token(token: str, key: SecretStr) -> str:
    return hmac.new(
        key=key.get_secret_value().encode(),
        msg=token.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
