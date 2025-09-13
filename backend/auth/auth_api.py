from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .types.auth_types import GoogleAuthRequest, UserResponse, LoginResponse, TokenData
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import uuid
import sys
import os

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

# Optional Google OAuth imports for production
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

# Mock database - replace with actual database later
MOCK_USERS_DB = {}

def verify_google_token(id_token_str: str) -> dict:
    """Verify Google ID token and return user info"""
    try:
        if GOOGLE_AUTH_AVAILABLE:
            # Production: Real Google token verification
            idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), settings.GOOGLE_CLIENT_ID)
            return idinfo
        else:
            # Development: Mock verification when Google libraries not available
            # This should be replaced with actual Google token verification in production
            mock_user_info = {
                'sub': 'google_user_123',  # Google user ID
                'email': 'user@example.com',
                'given_name': 'John',
                'family_name': 'Doe',
                'picture': 'https://example.com/profile.jpg'
            }
            return mock_user_info
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}"
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user lookup - replace with actual database query
    user = MOCK_USERS_DB.get(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse(**user)

@router.post("/google", 
             response_model=LoginResponse,
             summary="Google OAuth Authentication",
             description="Authenticate or register a user using Google OAuth ID token",
             response_description="JWT access token and user information",
             responses={
                 200: {
                     "description": "Successful authentication",
                     "content": {
                         "application/json": {
                             "example": {
                                 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                 "token_type": "bearer",
                                 "user": {
                                     "id": "uuid-string",
                                     "email": "user@gmail.com",
                                     "first_name": "John",
                                     "last_name": "Doe",
                                     "google_id": "google_user_123",
                                     "profile_picture": "https://lh3.googleusercontent.com/...",
                                     "created_at": "2024-01-01T00:00:00",
                                     "is_active": True
                                 },
                                 "is_new_user": False
                             }
                         }
                     }
                 },
                 401: {
                     "description": "Invalid Google ID token",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Invalid Google ID token: Token verification failed"}
                         }
                     }
                 }
             })
async def google_auth(auth_request: GoogleAuthRequest):
    """
    Authenticate or register a user using Google OAuth ID token.
    
    This endpoint handles both login and registration:
    - If the user exists (by Google ID), they are logged in
    - If the user doesn't exist, a new account is created
    
    Args:
        auth_request (GoogleAuthRequest): Contains the Google ID token
        
    Returns:
        LoginResponse: JWT access token, user information, and new user flag
        
    Raises:
        HTTPException: 401 if the Google ID token is invalid
    """
    # Verify Google ID token
    google_user_info = verify_google_token(auth_request.id_token)
    
    google_id = google_user_info['sub']
    email = google_user_info['email']
    first_name = google_user_info.get('given_name', '')
    last_name = google_user_info.get('family_name', '')
    profile_picture = google_user_info.get('picture')
    
    # Check if user already exists by Google ID
    existing_user = None
    existing_user_id = None
    
    for uid, user_data in MOCK_USERS_DB.items():
        if user_data.get("google_id") == google_id:
            existing_user = user_data
            existing_user_id = uid
            break
    
    is_new_user = False
    
    if existing_user:
        # User exists - login
        user_id = existing_user_id
        user = existing_user
    else:
        # New user - register
        is_new_user = True
        user_id = str(uuid.uuid4())
        
        user = {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "google_id": google_id,
            "profile_picture": profile_picture,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        MOCK_USERS_DB[user_id] = user
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(**user)
    
    return LoginResponse(
        access_token=access_token,
        user=user_response,
        is_new_user=is_new_user
    )

@router.get("/me", 
            response_model=UserResponse,
            summary="Get Current User",
            description="Get information about the currently authenticated user",
            response_description="Current user's profile information",
            responses={
                200: {
                    "description": "User information retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "id": "uuid-string",
                                "email": "user@gmail.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "google_id": "google_user_123",
                                "profile_picture": "https://lh3.googleusercontent.com/...",
                                "created_at": "2024-01-01T00:00:00",
                                "is_active": True
                            }
                        }
                    }
                },
                401: {
                    "description": "Authentication required",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Could not validate credentials"}
                        }
                    }
                }
            })
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.
    
    Requires a valid JWT token in the Authorization header.
    
    Args:
        current_user: Injected current user from JWT token
        
    Returns:
        UserResponse: Current user's profile information
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    return current_user
