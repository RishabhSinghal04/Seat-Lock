import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from pydantic import ValidationError

from app.core import Config
from app.core.enums import TokenClaims, TokenType
from app.core.exceptions.auth import InvalidTokenError, TokenExpiredError
from app.schemas import TokenPayload


@dataclass(frozen=True, slots=True)
class IssuedToken:
    token: str
    payload: TokenPayload


class TokenService:
    def __init__(self, config: Config) -> None:
        self.config = config

    def create_access_token(self, user_id: uuid.UUID) -> IssuedToken:
        return self._encode(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            expires_delta=timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    def create_refresh_token(self, user_id: uuid.UUID) -> IssuedToken:
        return self._encode(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            expires_delta=timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS),
        )

    def decode_token(self, token: str, expected_type: TokenType) -> TokenPayload:
        try:
            claims = jwt.decode(
                jwt=token,
                key=self.config.JWT_KEY.get_secret_value(),
                algorithms=[self.config.ALGORITHM],
                options={
                    "require": [
                        TokenClaims.JWT_ID,
                        TokenClaims.SUBJECT,
                        TokenClaims.TYPE,
                        TokenClaims.ISSUED_AT,
                        TokenClaims.EXPIRY,
                    ]
                },
                leeway=timedelta(seconds=10),
            )
            payload: TokenPayload = TokenPayload.model_validate(claims)
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError from exc
        except (jwt.InvalidTokenError, ValidationError) as exc:
            raise InvalidTokenError from exc

        if payload.token_type is not expected_type:
            raise InvalidTokenError
        return payload

    def _encode(
        self, user_id: uuid.UUID, token_type: TokenType, expires_delta: timedelta
    ) -> IssuedToken:
        now: datetime = datetime.now(UTC).replace(microsecond=0)
        payload = TokenPayload(
            jwt_id=uuid.uuid7(),
            user_id=user_id,
            token_type=token_type,
            issued_at=now,
            expires_at=now + expires_delta,
        )
        token: str = jwt.encode(
            payload=payload.model_dump(mode="json", by_alias=True),
            key=self.config.JWT_KEY.get_secret_value(),
            algorithm=self.config.ALGORITHM,
        )
        return IssuedToken(token=token, payload=payload)
