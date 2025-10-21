from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v and len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip() if v else v
