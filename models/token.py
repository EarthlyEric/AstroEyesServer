from pydantic import BaseModel, Field
from enum import Enum

class RefreshTokenBase(BaseModel):
    device_id: str = Field(max_length=64)
    refresh_token: str = Field()

class RevokeRefreshToken(RefreshTokenBase):
    pass

class RefreshType(str, Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"

class RefreshToken(RefreshTokenBase):
    type: RefreshType