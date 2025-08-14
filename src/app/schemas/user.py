from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    pass

class UserUpdate(UserBase):
    pass

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserOut(UserBase):
    id: int
    
    class Config:
        from_attributes = True # Pydantic v2 compatibility