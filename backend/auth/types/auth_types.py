from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
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

    model_config = ConfigDict(
        from_attributes=True)
    
    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, dt: datetime, _info):
        # ISO8601 without microseconds, always with Z
        return dt.replace(microsecond=0).isoformat() + "Z"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_new_user: bool = False

class TokenData(BaseModel):
    user_id: Optional[str] = None
