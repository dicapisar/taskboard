# Import necessary modules from Pydantic for data validation
from pydantic import BaseModel, EmailStr

# ---------------------------- BASE SCHEMA: UserBase ----------------------------

class UserBase(BaseModel):
    """
    Base model that defines shared fields for user data.
    This class is used as a parent for other user schemas.
    """

    username: str         # Username chosen by the user
    email: EmailStr       # User's email address (validated as a valid email format)

# ---------------------------- SCHEMA: UserCreate ----------------------------

class UserCreate(UserBase):
    """
    Schema used when creating a new user.
    Inherits username and email from UserBase.
    """

    password: str         # Password set by the user during registration
    pass                  # Placeholder, does nothing (can be removed safely)

# ---------------------------- SCHEMA: UserUpdate ----------------------------

class UserUpdate(UserBase):
    """
    Schema used for updating a user's profile.
    Inherits fields from UserBase. No additional fields.
    """
    pass

# ---------------------------- SCHEMA: UserPasswordUpdate ----------------------------

class UserPasswordUpdate(BaseModel):
    """
    Schema used when a user wants to change their password.
    """

    old_password: str     # The user's current password
    new_password: str     # The new password the user wants to set

# ---------------------------- SCHEMA: UserOut ----------------------------

class UserOut(UserBase):
    """
    Schema used to return user data to the client.
    Includes user ID along with username and email.
    """

    id: int               # Unique identifier of the user

    class Config:
        from_attributes = True  # Enables creation from ORM models (Pydantic v2 compatibility)