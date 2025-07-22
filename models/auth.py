from pydantic import BaseModel, Field

class UserBase(BaseModel):
    """
    Base model for user authentication.
    Fields:
        username: 8-32 characters, allows only letters, numbers, and underscores.
        password: 8-128 characters, allows letters, numbers, and common special characters.
    """
    username: str = Field(min_length=8, max_length=32, pattern=r"^[a-zA-Z0-9_]+$") 
    password: str = Field( min_length=8, max_length=128, pattern=r'^[a-zA-Z0-9!"#$%&\'()*+,\-./:;<=>?@\[\]\\^_`{|}~]+$')
    
class UserRegister(UserBase):
    """
    Model for user registration.
    Fields:
        invite_code: Optional invite code for registration.
    """
    display_name: str = Field(min_length=1, max_length=32)
    invite_code: str | None = None
    
class UserLogin(UserBase):
    """
    Model for user login.
    Inherits from UserBase.
    """
    pass
