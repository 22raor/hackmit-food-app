from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class GoogleAuthRequest(BaseModel):
    id_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    google_id: str
    profile_picture: Optional[str] = None
    created_at: datetime
    is_active: bool

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_new_user: bool = False

class TokenData(BaseModel):
    user_id: Optional[str] = None
