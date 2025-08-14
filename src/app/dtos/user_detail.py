from dataclasses import dataclass

@dataclass
class UserDetail:
    id: int
    username: str
    email: str
    is_admin: bool = False
