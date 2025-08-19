# Import required types from Pydantic
from pydantic import BaseModel, EmailStr

# ---------------------------- Login Schema ----------------------------

class Login(BaseModel):
    """
    This model is used to validate login credentials sent by the user.
    """

    email: EmailStr     # The user's email address; must be a valid email format
    password: str       # The user's password as plain text (to be validated during login)