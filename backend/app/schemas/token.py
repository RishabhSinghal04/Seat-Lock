import uuid
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_serializer

from app.core.enums import TokenClaims, TokenType


class TokenPayload(BaseModel):
    model_config = ConfigDict(frozen=True, validate_by_name=True)

    jwt_id: uuid.UUID = Field(alias=TokenClaims.JWT_ID)
    user_id: uuid.UUID = Field(alias=TokenClaims.SUBJECT)
    token_type: TokenType = Field(alias=TokenClaims.TYPE)
    issued_at: AwareDatetime = Field(alias=TokenClaims.ISSUED_AT)
    expires_at: AwareDatetime = Field(alias=TokenClaims.EXPIRY)

    @field_serializer("issued_at", "expires_at")
    def _to_epoch(self, value: datetime) -> int:
        return int(value.timestamp())


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type = "bearer"
