from pydantic import BaseModel, EmailStr
from typing import Optional

class AuthResponseDto(BaseModel):
    message: str
    email: EmailStr
    role: str
    token: Optional[str] = None
