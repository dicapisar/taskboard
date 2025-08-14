from dataclasses import dataclass

@dataclass
class UserDetail:
    id: int
    username: str
    email: str
    is_superuser: bool = False
