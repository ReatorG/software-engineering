from pydantic import BaseModel, EmailStr
from typing import Optional

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role_id: int
    role_name: str
    role_description: Optional[str] = None
    is_active: bool

    @property
    def role(self) -> RoleResponse:
        return RoleResponse(
            id=self.role_id,
            name=self.role_name,
            description=self.role_description
        )


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
