# Import the dataclass decorator to simplify class creation
from dataclasses import dataclass

# ---------------------------- User Detail Data Structure ----------------------------

@dataclass
class UserDetail:
    """
    This data class represents the details of a user.
    It is used to store and transfer user information such as ID, username, and email.
    """

    id: int              # Unique identifier for the user
    username: str        # Username chosen by the user
    email: str           # User's email address
    is_admin: bool = False  # Whether the user has administrative privileges (default: False)