from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .types.auth_types import UserRegister, UserLogin, UserResponse, LoginResponse, TokenData
import jwt
from datetime import datetime, timedelta
import bcrypt
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

MOCK_USERS_DB = {}
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except jwt.PyJWTError:
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

@router.post("/register", response_model=LoginResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if user already exists
    for user in MOCK_USERS_DB.values():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    user_id = f"user_{len(MOCK_USERS_DB) + 1}"
    hashed_password = hash_password(user_data.password)
    
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    MOCK_USERS_DB[user_id] = new_user
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(**{k: v for k, v in new_user.items() if k != "password"})
    
    return LoginResponse(
        access_token=access_token,
        user=user_response
    )

@router.post("/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin):
    """Login user and return JWT token"""
    # Find user by email
    user = None
    user_id = None
    for uid, user_data in MOCK_USERS_DB.items():
        if user_data["email"] == user_credentials.email:
            user = user_data
            user_id = uid
            break
    
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(**{k: v for k, v in user.items() if k != "password"})
    
    return LoginResponse(
        access_token=access_token,
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user
