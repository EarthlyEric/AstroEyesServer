from pydantic import BaseModel, Field

class UserAccessTokenBase(BaseModel):
    access_token: str = Field()
    device_id: str = Field(max_length=64)

class UserRevokeAccessToken(UserAccessTokenBase):
    pass

class UserRefreshToken(UserAccessTokenBase):
    pass