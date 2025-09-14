from fastapi import APIRouter, HTTPException, Depends, status
from .types.recs_types import RecommendationRequest, RecommendationResponse, FoodItemRecommendation, RecommendationContext
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from config import settings
from user_profile.profile_api import MOCK_PROFILES_DB
from food_info.info_api import get_restaurant_by_id
from util.chat.gpt_client import ClaudeClient
import uuid
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/recs", tags=["recommendations"])

# Initialize Claude client
claude_client = ClaudeClient(settings.ANTHROPIC_API_KEY)


def get_user_profile_data(user_id: str) -> Dict[str, Any]:
    """Get user profile data from database and convert to dict format"""
    user_profile_data = MOCK_PROFILES_DB.get(user_id)

    if not user_profile_data:
        return {
            "dietary_restrictions": [],
            "cuisine_preferences": [],
            "flavor_profile": {},
            "liked_foods": [],
            "disliked_foods": []
        }

    # Convert Pydantic models to dicts safely
    return {
        "dietary_restrictions": [
            dr.dict() if hasattr(dr, 'dict') else dr
            for dr in user_profile_data.dietary_restrictions
        ],
        "cuisine_preferences": [
            cp.dict() if hasattr(cp, 'dict') else cp
            for cp in user_profile_data.cuisine_preferences
        ],
        "flavor_profile": (
            user_profile_data.flavor_profile.dict()
            if user_profile_data.flavor_profile and hasattr(user_profile_data.flavor_profile, 'dict')
            else user_profile_data.flavor_profile or {}
        ),
        "liked_foods": [
            lf.dict() if hasattr(lf, 'dict') else lf
            for lf in user_profile_data.liked_foods
        ],
        "disliked_foods": [
            df.dict() if hasattr(df, 'dict') else df
            for df in user_profile_data.disliked_foods
        ]
    }


def get_restaurant_data(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Get restaurant data from in-memory cache"""
    return get_restaurant_by_id(restaurant_id)


def gather_recommendation_context(
    user_id: str,
    restaurant_id: str,
    curr_dislikes: List[str]
) -> RecommendationContext:
    """Gather all context needed for AI recommendation"""

    # Get user profile
    user_profile = get_user_profile_data(user_id)

    # Get restaurant data from cache
    restaurant_data = get_restaurant_data(restaurant_id)

    if not restaurant_data:
        # Return empty context if restaurant not found
        return RecommendationContext(
            user_profile=user_profile,
            restaurant_items=[],
            restaurant_reviews=[],
            top_community_items=[],
            current_dislikes=curr_dislikes,
            session_history=[]
        )

    # Extract data from the cached restaurant data
    restaurant_items = restaurant_data.get("menu_items", [])
    restaurant_reviews = restaurant_data.get("reviews", [])
    top_community_items = restaurant_data.get("top_items", [])

    return RecommendationContext(
        user_profile=user_profile,
        restaurant_items=restaurant_items,
        restaurant_reviews=restaurant_reviews,
        top_community_items=top_community_items,
        current_dislikes=curr_dislikes,
        session_history=[]
    )


@router.post("/{restaurant_id}",
             response_model=RecommendationResponse,
             summary="Get AI Food Recommendation",
             description="Get a personalized food recommendation using AI analysis of user preferences, restaurant menu, and community data",
             response_description="AI-generated food recommendation with reasoning and confidence score")
async def get_recommendation(
    restaurant_id: str,
    request: RecommendationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate a personalized food recommendation using AI.

    Analyzes user taste profile, current dislikes, restaurant menu, reviews,
    and community data to suggest the best food item with detailed reasoning.
    """
    try:
        # Check if restaurant exists
        restaurant_data = get_restaurant_data(restaurant_id)
        if not restaurant_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )

        # Gather all context for the recommendation
        context = gather_recommendation_context(
            current_user.id,
            restaurant_id,
            request.curr_dislikes
        )

        # Get restaurant name from cached data
        restaurant_name = restaurant_data.get("name", f"Restaurant {restaurant_id}")

        # Generate recommendation using Claude
        claude_response = await claude_client.generate_food_recommendation(
            user_profile=context.user_profile,
            restaurant_items=context.restaurant_items,
            reviews=context.restaurant_reviews,
            community_favorites=context.top_community_items,
            current_dislikes=context.current_dislikes,
            restaurant_name=restaurant_name
        )

        # Convert Claude response to FoodItemRecommendation
        recommendation = FoodItemRecommendation(
            id=f"claude_rec_{uuid.uuid4()}",
            name=claude_response.get("recommended_item", "Chef's Special"),
            description="AI-recommended item based on your preferences",
            price=claude_response.get("price", 15.99),  # Default price - could extract from menu data
            image_url=claude_response.get("image_url", "https://example.com/default_image.jpg"),
            category=claude_response.get("category", "AI Recommendation"),
            ingredients=[],
            allergens=[],
            calories=300,
            reviews=[],
            reasoning=claude_response.get("reasoning", "Recommended by our AI based on your taste profile")
        )

        return RecommendationResponse(
            item=recommendation,
            confidence_score=claude_response.get("confidence", 0.85),
            session_id=str(uuid.uuid4()),
            alternatives=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}"
        )


@router.get("/{restaurant_id}/context",
            summary="Get Recommendation Context",
            description="Retrieve the data context used for generating recommendations (useful for debugging)",
            response_description="Summary of user profile, restaurant data, and community insights")
async def get_recommendation_context(
    restaurant_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the data context used for generating recommendations.

    Useful for debugging and understanding how the AI makes decisions.
    """
    try:
        # Check if restaurant exists
        restaurant_data = get_restaurant_data(restaurant_id)
        if not restaurant_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )

        context = gather_recommendation_context(
            current_user.id,
            restaurant_id,
            []
        )

        return {
            "user_profile_summary": context.user_profile,
            "available_items_count": len(context.restaurant_items),
            "reviews_count": len(context.restaurant_reviews),
            "community_favorites_count": len(context.top_community_items),
            "restaurant_info": {
                "id": restaurant_data.get("id"),
                "name": restaurant_data.get("name"),
                "average_rating": restaurant_data.get("average_rating"),
                "tags": restaurant_data.get("tags", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendation context: {str(e)}"
        )
