from pydantic import BaseModel, Field, field_validator
from utils.validator import validate_password_strength

class userBase(BaseModel):
    """
    Base model for user authentication.
    Fields:
        username: 8-32 characters, allows only letters, numbers, and underscores.
        password: 8-128 characters, allows letters, numbers, and common special characters.
    """
    username: str = Field(min_length=8, max_length=32, pattern=r"^[a-zA-Z0-9_]+$") 
    password: str = Field(min_length=8, max_length=128)
    
    @field_validator("password")
    def validate_password_strength(cls, v):
        return validate_password_strength(v)

class userRegister(userBase):
    """
    Model for user registration.
    Fields:
        display_name: 1-32 characters, allows letters, numbers, and underscores.
        invite_code: Optional invite code for registration.
    """
    display_name: str = Field(min_length=1, max_length=32)
    invite_code: str | None = None

class userLogin(userBase):
    """
    Model for user login.
    Inherits from UserBase.
    """
    device_id: str  = Field(max_length=64)
