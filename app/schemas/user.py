from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr 
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    model_config = {
        "from_attributes": True
    }
    
class Token(BaseModel):
    access_token: str
    token_type: str