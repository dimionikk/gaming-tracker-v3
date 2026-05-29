from pydantic import BaseModel
from uuid import UUID
class UserCreate(BaseModel):
    username:str
    email:str
    password:str

class UserLogin(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id:UUID
    username:str
    email:str

class Token(BaseModel):
    access_token: str
    token_type: str