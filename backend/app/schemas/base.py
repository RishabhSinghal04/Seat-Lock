from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class MessageResponse(BaseResponse):
    message: str
