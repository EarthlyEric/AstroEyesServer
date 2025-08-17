from pydantic import BaseModel, Field, field_validator
from typing import Optional
from utils.validator import validate_password_strength

class updateProfile(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=32)
    
class updatePassword(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("new_password")
    def validate_password_strength(cls, v):
        return validate_password_strength(v)
