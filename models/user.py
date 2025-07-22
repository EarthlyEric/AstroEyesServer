from pydantic import BaseModel, Field
from typing import Optional

class updateUser(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=32)
    
class updateUserPassword(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=128, pattern=r'^[a-zA-Z0-9!"#$%&\'()*+,\-./:;<=>?@\[\]\\^_`{|}~]+$')
    new_password: str = Field(..., min_length=8, max_length=128, pattern=r'^[a-zA-Z0-9!"#$%&\'()*+,\-./:;<=>?@\[\]\\^_`{|}~]+$')
