from fastapi import APIRouter, HTTPException, Depends, status
from .types.profile_types import UserTasteProfile, UpdateTasteProfile, TasteProfileResponse
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/user_profile", tags=["user_profile"])

# Mock database for user profiles - replace with actual database later
MOCK_PROFILES_DB: Dict[str, UserTasteProfile] = {}

@router.get("/{user_id}", response_model=TasteProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's taste profile"""
    # Check if user is accessing their own profile or has permission
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    profile = MOCK_PROFILES_DB.get(user_id)
    if not profile:
        # Create default profile if none exists
        profile = UserTasteProfile(
            user_id=user_id,
            dietary_restrictions=[],
            cuisine_preferences=[],
            flavor_profile=None,
            liked_foods=[],
            disliked_foods=[],
            favorite_restaurants=[],
            price_range_preference=None,
            meal_time_preferences={},
            updated_at=datetime.utcnow()
        )
        MOCK_PROFILES_DB[user_id] = profile
    
    return TasteProfileResponse(
        profile=profile,
        recommendations_count=len(profile.liked_foods) + len(profile.disliked_foods),
        last_activity=profile.updated_at
    )

@router.post("/{user_id}", response_model=TasteProfileResponse)
async def update_user_profile(
    user_id: str,
    profile_update: UpdateTasteProfile,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user's taste profile"""
    # Check if user is updating their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Get existing profile or create new one
    existing_profile = MOCK_PROFILES_DB.get(user_id)
    if not existing_profile:
        existing_profile = UserTasteProfile(
            user_id=user_id,
            dietary_restrictions=[],
            cuisine_preferences=[],
            flavor_profile=None,
            liked_foods=[],
            disliked_foods=[],
            favorite_restaurants=[],
            price_range_preference=None,
            meal_time_preferences={},
            updated_at=datetime.utcnow()
        )
    
    # Update fields that are provided
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(existing_profile, field, value)
    
    existing_profile.updated_at = datetime.utcnow()
    MOCK_PROFILES_DB[user_id] = existing_profile
    
    return TasteProfileResponse(
        profile=existing_profile,
        recommendations_count=len(existing_profile.liked_foods) + len(existing_profile.disliked_foods),
        last_activity=existing_profile.updated_at
    )

@router.delete("/{user_id}")
async def delete_user_profile(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete user's taste profile"""
    # Check if user is deleting their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this profile"
        )
    
    if user_id in MOCK_PROFILES_DB:
        del MOCK_PROFILES_DB[user_id]
        return {"message": "Profile deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
