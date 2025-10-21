from pydantic import BaseModel

class UpdateRoleRequest(BaseModel):
    role_id: int
