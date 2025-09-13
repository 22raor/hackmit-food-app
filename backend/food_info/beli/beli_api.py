from fastapi import APIRouter, HTTPException, status, Depends
from .types.beli_types import BeliTopItem, BeliRestaurantTopItems, BeliUserProfile, BeliUserRestaurantReview
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/beli", tags=["beli"])

# Mock data - replace with actual Beli API calls later
MOCK_RESTAURANT_TOP_ITEMS = {
    "rest_1": BeliRestaurantTopItems(
        restaurant_id="rest_1",
        restaurant_name="Sakura Sushi",
        top_items=[
            BeliTopItem(
                name="Dragon Roll",
                photo_url="https://example.com/dragon-roll.jpg",
                recommendation_count=23
            ),
            BeliTopItem(
                name="Salmon Sashimi",
                photo_url="https://example.com/salmon-sashimi.jpg",
                recommendation_count=18
            ),
            BeliTopItem(
                name="Miso Soup",
                photo_url="https://example.com/miso-soup.jpg",
                recommendation_count=12
            )
        ],
        last_updated=datetime.utcnow()
    ),
    "rest_2": BeliRestaurantTopItems(
        restaurant_id="rest_2",
        restaurant_name="Tony's Pizza",
        top_items=[
            BeliTopItem(
                name="Margherita Pizza",
                photo_url="https://example.com/margherita.jpg",
                recommendation_count=31
            ),
            BeliTopItem(
                name="Pepperoni Pizza",
                photo_url="https://example.com/pepperoni.jpg",
                recommendation_count=27
            ),
            BeliTopItem(
                name="Caesar Salad",
                photo_url="https://example.com/caesar-salad.jpg",
                recommendation_count=15
            )
        ],
        last_updated=datetime.utcnow()
    )
}

MOCK_USER_PROFILES = {
    "user_1": BeliUserProfile(
        user_id="user_1",
        username="foodie_sarah",
        restaurant_reviews=[
            BeliUserRestaurantReview(
                restaurant_name="Sakura Sushi",
                restaurant_id="rest_1",
                rating=9,
                notes="Amazing sushi! Fresh ingredients and creative rolls.",
                date_reviewed=datetime.utcnow()
            ),
            BeliUserRestaurantReview(
                restaurant_name="Tony's Pizza",
                restaurant_id="rest_2",
                rating=7,
                notes="Good pizza but service was slow.",
                date_reviewed=datetime.utcnow()
            ),
            BeliUserRestaurantReview(
                restaurant_name="Thai Garden",
                restaurant_id="rest_3",
                rating=8,
                notes="Authentic flavors, great pad thai."
            )
        ],
        total_reviews=3,
        last_updated=datetime.utcnow()
    )
}

@router.get("/restaurant/{restaurant_id}/top_items", response_model=BeliRestaurantTopItems)
async def get_restaurant_top_items(
    restaurant_id: str,
    limit: Optional[int] = 10,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get top recommended items at a restaurant from Beli"""
    # Mock implementation - replace with actual Beli API call
    restaurant_data = MOCK_RESTAURANT_TOP_ITEMS.get(restaurant_id)
    
    if not restaurant_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Beli data found for restaurant {restaurant_id}"
        )
    
    # Apply limit to top items if specified
    if limit and len(restaurant_data.top_items) > limit:
        limited_items = restaurant_data.top_items[:limit]
        return BeliRestaurantTopItems(
            restaurant_id=restaurant_data.restaurant_id,
            restaurant_name=restaurant_data.restaurant_name,
            top_items=limited_items,
            last_updated=restaurant_data.last_updated
        )
    
    return restaurant_data


@router.get("/user/{user_id}/profile", response_model=BeliUserProfile)
async def get_user_profile(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a user's Beli profile with restaurant reviews"""
    # Mock implementation - replace with actual Beli API call
    profile = MOCK_USER_PROFILES.get(user_id)
    if not profile:
        # Return empty profile if user not found
        return BeliUserProfile(
            user_id=user_id,
            username="unknown_user",
            restaurant_reviews=[],
            total_reviews=0,
            last_updated=datetime.utcnow()
        )
    
    return profile

@router.get("/user/{user_id}/reviews", response_model=List[BeliUserRestaurantReview])
async def get_user_restaurant_reviews(
    user_id: str,
    limit: Optional[int] = 20,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all restaurant reviews by a specific user from Beli"""
    # Mock implementation - replace with actual Beli API call
    profile = MOCK_USER_PROFILES.get(user_id)
    if not profile:
        return []
    
    reviews = profile.restaurant_reviews
    if limit:
        reviews = reviews[:limit]
    
    return reviews
