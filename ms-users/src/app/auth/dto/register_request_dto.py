from pydantic import BaseModel, EmailStr,field_validator

class RegisterRequestDto(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role_id: int

    @field_validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
