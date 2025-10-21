from dataclasses import dataclass
from .role import Role

@dataclass
class User:
    id: int | None
    first_name: str
    last_name: str
    email: str
    password: str
    role: Role
    is_active: bool = True
