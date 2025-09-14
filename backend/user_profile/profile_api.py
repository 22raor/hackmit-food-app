from fastapi import APIRouter, HTTPException, Depends, status
from .types.profile_types import UserTasteProfile, UpdateTasteProfile, TasteProfileResponse
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/user_profile", tags=["user_profile"])

# Mock database for user profiles - replace with actual database later
MOCK_PROFILES_DB: Dict[str, UserTasteProfile] = {}

@router.get("/{user_id}", 
           response_model=TasteProfileResponse,
           summary="Get User Taste Profile",
           description="Retrieve a user's complete taste profile including preferences and food history",
           response_description="User's taste profile with activity statistics",
           responses={
               200: {
                   "description": "Taste profile retrieved successfully",
                   "content": {
                       "application/json": {
                           "example": {
                               "profile": {
                                   "user_id": "uuid-string",
                                   "dietary_restrictions": ["vegetarian", "gluten-free"],
                                   "cuisine_preferences": ["italian", "mexican", "thai"],
                                   "flavor_profile": "spicy",
                                   "liked_foods": ["pasta", "tacos", "pad thai"],
                                   "disliked_foods": ["mushrooms", "olives"],
                                   "favorite_restaurants": ["restaurant_id_1", "restaurant_id_2"],
                                   "price_range_preference": "medium",
                                   "meal_time_preferences": {"breakfast": ["light"], "dinner": ["hearty"]},
                                   "updated_at": "2024-01-01T00:00:00"
                               },
                               "recommendations_count": 15,
                               "last_activity": "2024-01-01T00:00:00"
                           }
                       }
                   }
               },
               403: {
                   "description": "Access forbidden",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Not authorized to access this profile"}
                       }
                   }
               }
           })
async def get_user_profile(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve a user's complete taste profile.
    
    Returns the user's dietary restrictions, cuisine preferences, liked/disliked foods,
    favorite restaurants, and other preference data. Users can only access their own profiles.
    
    Args:
        user_id (str): The ID of the user whose profile to retrieve
        current_user: Injected current user from JWT token
        
    Returns:
        TasteProfileResponse: Complete taste profile with activity statistics
        
    Raises:
        HTTPException: 403 if user tries to access another user's profile
    """
    # Check if user is accessing their own profile or has permission
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    profile = MOCK_PROFILES_DB.get(user_id)
    print(f"DEBUG: GET - Looking for profile for user {user_id}")
    print(f"DEBUG: GET - MOCK_PROFILES_DB keys: {list(MOCK_PROFILES_DB.keys())}")
    print(f"DEBUG: GET - Found profile: {profile is not None}")
    
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
        print(f"DEBUG: GET - Created new default profile for {user_id}")
    else:
        print(f"DEBUG: GET - Retrieved existing profile: {profile.dict()}")
    
    return TasteProfileResponse(
        profile=profile,
        recommendations_count=len(profile.liked_foods) + len(profile.disliked_foods),
        last_activity=profile.updated_at
    )

@router.post("/{user_id}", 
            response_model=TasteProfileResponse,
            summary="Update User Taste Profile",
            description="Update a user's taste profile with new preferences and food history",
            response_description="Updated taste profile with activity statistics",
            responses={
                200: {
                    "description": "Profile updated successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "profile": {
                                    "user_id": "uuid-string",
                                    "dietary_restrictions": ["vegetarian"],
                                    "cuisine_preferences": ["italian", "mexican"],
                                    "flavor_profile": "mild",
                                    "liked_foods": ["pasta", "pizza"],
                                    "disliked_foods": ["mushrooms"],
                                    "favorite_restaurants": ["restaurant_id_1"],
                                    "price_range_preference": "medium",
                                    "meal_time_preferences": {"lunch": ["quick"]},
                                    "updated_at": "2024-01-01T12:00:00"
                                },
                                "recommendations_count": 8,
                                "last_activity": "2024-01-01T12:00:00"
                            }
                        }
                    }
                },
                403: {
                    "description": "Access forbidden",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Not authorized to update this profile"}
                        }
                    }
                }
            })
async def update_user_profile(
    user_id: str,
    profile_update: UpdateTasteProfile,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update a user's taste profile with new preferences.
    
    Allows partial updates - only provided fields will be updated.
    Users can only update their own profiles.
    
    Args:
        user_id (str): The ID of the user whose profile to update
        profile_update (UpdateTasteProfile): Profile fields to update
        current_user: Injected current user from JWT token
        
    Returns:
        TasteProfileResponse: Updated taste profile with activity statistics
        
    Raises:
        HTTPException: 403 if user tries to update another user's profile
    """
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
    print(f"DEBUG: Updating profile for user {user_id} with data: {update_data}")
    
    for field, value in update_data.items():
        if value is not None:
            print(f"DEBUG: Setting {field} to {value}")
            setattr(existing_profile, field, value)
    
    existing_profile.updated_at = datetime.utcnow()
    MOCK_PROFILES_DB[user_id] = existing_profile
    
    print(f"DEBUG: Profile after update: {existing_profile.dict()}")
    print(f"DEBUG: MOCK_PROFILES_DB keys: {list(MOCK_PROFILES_DB.keys())}")
    
    return TasteProfileResponse(
        profile=existing_profile,
        recommendations_count=len(existing_profile.liked_foods) + len(existing_profile.disliked_foods),
        last_activity=existing_profile.updated_at
    )

@router.delete("/{user_id}",
              summary="Delete User Taste Profile",
              description="Permanently delete a user's taste profile and all associated data",
              response_description="Confirmation message",
              responses={
                  200: {
                      "description": "Profile deleted successfully",
                      "content": {
                          "application/json": {
                              "example": {"message": "Profile deleted successfully"}
                          }
                      }
                  },
                  403: {
                      "description": "Access forbidden",
                      "content": {
                          "application/json": {
                              "example": {"detail": "Not authorized to delete this profile"}
                          }
                      }
                  },
                  404: {
                      "description": "Profile not found",
                      "content": {
                          "application/json": {
                              "example": {"detail": "Profile not found"}
                          }
                      }
                  }
              })
async def delete_user_profile(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Permanently delete a user's taste profile.
    
    This action cannot be undone. All taste preferences, food history,
    and recommendation data will be permanently removed.
    
    Args:
        user_id (str): The ID of the user whose profile to delete
        current_user: Injected current user from JWT token
        
    Returns:
        dict: Confirmation message
        
    Raises:
        HTTPException: 403 if user tries to delete another user's profile
        HTTPException: 404 if profile doesn't exist
    """
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
