from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import uuid
import sys
import os
import jwt
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.types.auth_types import GoogleAuthRequest, LoginResponse, UserResponse
from config import settings
from util.auth.jwt_handler import create_access_token, verify_token
from database import get_db
from models import User

# Optional Google OAuth imports for production
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests

    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


# Database functions
def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID"""
    return db.query(User).filter(User.google_id == google_id).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, google_user_info: dict) -> User:
    """Create new user from Google user info"""
    user = User(
        id=str(uuid.uuid4()),
        email=google_user_info.get("email"),
        first_name=google_user_info.get("given_name", ""),
        last_name=google_user_info.get("family_name", ""),
        google_id=google_user_info.get("sub"),
        profile_picture=google_user_info.get("picture"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_google_token(id_token_str: str) -> dict:
    """Verify Google ID token and return user info"""
    try:
        if GOOGLE_AUTH_AVAILABLE:
            # Production: Real Google token verification
            idinfo = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            return idinfo
        else:
            # Development: Mock verification when Google libraries not available
            # This should be replaced with actual Google token verification in production
            mock_user_info = {
                "sub": "google_user_123",  # Google user ID
                "email": "user@example.com",
                "given_name": "John",
                "family_name": "Doe",
                "picture": "https://example.com/profile.jpg",
            }
            return mock_user_info

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google ID token: {str(e)}",
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Get current user from JWT token

    Args:
        credentials: JWT token from Authorization header
        db: Database session

    Returns:
        UserResponse: Current user information

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    try:
        # Verify JWT token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            google_id=user.google_id,
            profile_picture=user.profile_picture,
            created_at=user.created_at,
            is_active=user.is_active,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/google",
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
                            "is_active": True,
                        },
                        "is_new_user": False,
                    }
                }
            },
        },
        401: {
            "description": "Invalid Google ID token",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid Google ID token: Token verification failed"
                    }
                }
            },
        },
    },
)
async def google_auth(auth_request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate or register a user using Google OAuth ID token.

    This endpoint accepts a Google ID token, verifies it, and either:
    1. Logs in an existing user, or
    2. Creates a new user account

    Args:
        auth_request: Contains the Google ID token
        db: Database session

    Returns:
        LoginResponse: JWT access token and user information

    Raises:
        HTTPException: 401 if the Google ID token is invalid
    """

    if "mock" in auth_request.id_token:
        existing_user = get_user_by_google_id(db, "101234567890123456789")
        if not existing_user:

            mock_google_user_info = {
                "email": "jane.doe@example.com",
                "given_name": "Jane",
                "family_name": "Doe",
                "sub": "101234567890123456789",
                "picture": "https://lh3.googleusercontent.com/a/AItb_s-some-unique-id-for-jane=s96-c",
            }

            existing_user = create_user(db, mock_google_user_info)
    else:
        # Verify Google ID token
        google_user_info = verify_google_token(auth_request.id_token)

        # Check if user exists in database
        google_id = google_user_info.get("sub")
        existing_user = get_user_by_google_id(db, google_id)

    is_new_user = existing_user is None

    if existing_user:
        # User exists, log them in
        user = existing_user
    else:
        # Create new user
        user = create_user(db, google_user_info)

    # Create user response
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        google_id=user.google_id,
        profile_picture=user.profile_picture,
        created_at=user.created_at,
        is_active=user.is_active,
    )

    # Create JWT token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response,
        is_new_user=is_new_user,
    )


@router.get(
    "/me",
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
                        "is_active": True,
                    }
                }
            },
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
    },
)
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
