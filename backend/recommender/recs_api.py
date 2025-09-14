from fastapi import APIRouter, HTTPException, Depends, status
from .types.recs_types import (
    RecommendationRequest, 
    RecommendationResponse, 
    FoodItemRecommendation,
    RecommendationContext,
    GPTPromptData
)
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from datetime import datetime
from typing import List
import uuid
import json
import sys
import os
import httpx

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.chat.gpt_client import ClaudeClient
from config import settings

router = APIRouter(prefix="/recs", tags=["recommendations"])

# Initialize Claude client
claude_client = ClaudeClient(settings.ANTHROPIC_API_KEY)

# Mock recommendation engine - replace with actual Claude integration later
def generate_recommendation_mock(context: RecommendationContext, restaurant_id: str) -> FoodItemRecommendation:
    """Mock recommendation generation - replace with actual GPT call"""
    
    # Simple mock logic based on dislikes
    mock_items = [
        {
            "id": "rec_1",
            "name": "Spicy Tuna Roll",
            "description": "Fresh tuna with spicy mayo and cucumber",
            "price": 13.99,
            "category": "Sushi Rolls",
            "ingredients": ["tuna", "spicy mayo", "cucumber", "nori"],
            "allergens": ["fish"],
            "calories": 290,
            "reasoning": "Based on your preference for umami flavors and seafood, this spicy tuna roll offers the perfect balance of heat and freshness. The community rates it highly for its quality ingredients."
        },
        {
            "id": "rec_2", 
            "name": "Truffle Mushroom Pizza",
            "description": "Wood-fired pizza with truffle oil, wild mushrooms, and mozzarella",
            "price": 22.99,
            "category": "Pizza",
            "ingredients": ["truffle oil", "wild mushrooms", "mozzarella", "pizza dough"],
            "allergens": ["gluten", "dairy"],
            "calories": 340,
            "reasoning": "Given your sophisticated palate and preference for rich, earthy flavors, this truffle mushroom pizza represents the perfect elevated comfort food. Your friends have consistently rated similar items highly."
        }
    ]
    
    # Filter out disliked items
    available_items = [item for item in mock_items if item["name"] not in context.current_dislikes]
    
    if not available_items:
        # Fallback recommendation
        return FoodItemRecommendation(
            id="fallback_1",
            name="Chef's Special",
            description="Today's special recommendation from the chef",
            price=18.99,
            category="Specials",
            ingredients=["seasonal ingredients"],
            allergens=[],
            calories=300,
            reviews=[],
            reasoning="Since you've explored many options, I recommend trying the chef's special - it's often the most creative and well-executed dish."
        )
    
    # Select first available item for mock
    selected = available_items[0]
    
    return FoodItemRecommendation(
        id=selected["id"],
        name=selected["name"],
        description=selected["description"],
        price=selected["price"],
        category=selected["category"],
        ingredients=selected["ingredients"],
        allergens=selected["allergens"],
        calories=selected["calories"],
        reviews=[
            {
                "author": "foodie_mike",
                "rating": 5,
                "text": "Absolutely delicious! Highly recommend.",
                "date": "2024-01-15"
            }
        ],
        reasoning=selected["reasoning"]
    )

async def gather_recommendation_context(user_id: str, restaurant_id: str, curr_dislikes: List[str]) -> RecommendationContext:
    """Gather all context needed for AI recommendation by calling actual APIs"""
    
    async with httpx.AsyncClient() as client:
        base_url = f"http://localhost:{settings.PORT}"
        
        # Get user profile from user_profile API
        try:
            user_profile_response = await client.get(f"{base_url}/user_profile/{user_id}")
            user_profile = user_profile_response.json() if user_profile_response.status_code == 200 else {}
        except Exception:
            user_profile = {}
        
        # Get restaurant items from food_info API
        try:
            restaurant_items_response = await client.get(f"{base_url}/restaurants/{restaurant_id}/menu")
            restaurant_items = restaurant_items_response.json() if restaurant_items_response.status_code == 200 else []
        except Exception:
            restaurant_items = []
        
        # Get restaurant reviews from food_info API
        try:
            reviews_response = await client.get(f"{base_url}/restaurants/{restaurant_id}/reviews")
            restaurant_reviews = reviews_response.json() if reviews_response.status_code == 200 else []
        except Exception:
            restaurant_reviews = []
        
        # Get community top items from food_info API
        try:
            community_response = await client.get(f"{base_url}/restaurants/{restaurant_id}/community")
            top_community_items = community_response.json() if community_response.status_code == 200 else []
        except Exception:
            top_community_items = []
    
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
             response_description="AI-generated food recommendation with reasoning and confidence score",
             responses={
                 200: {
                     "description": "Recommendation generated successfully",
                     "content": {
                         "application/json": {
                             "example": {
                                 "item": {
                                     "id": "rec_1",
                                     "name": "Spicy Tuna Roll",
                                     "description": "Fresh tuna with spicy mayo and cucumber",
                                     "price": 13.99,
                                     "category": "Sushi Rolls",
                                     "ingredients": ["tuna", "spicy mayo", "cucumber", "nori"],
                                     "allergens": ["fish"],
                                     "calories": 290,
                                     "reviews": [
                                         {
                                             "author": "foodie_mike",
                                             "rating": 5,
                                             "text": "Absolutely delicious! Highly recommend.",
                                             "date": "2024-01-15"
                                         }
                                     ],
                                     "reasoning": "Based on your preference for umami flavors and seafood, this spicy tuna roll offers the perfect balance of heat and freshness."
                                 },
                                 "confidence_score": 0.85,
                                 "session_id": "uuid-string",
                                 "alternatives": []
                             }
                         }
                     }
                 },
                 500: {
                     "description": "Recommendation generation failed",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Failed to generate recommendation: AI service unavailable"}
                         }
                     }
                 }
             })
async def get_recommendation(
    restaurant_id: str,
    request: RecommendationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate a personalized food recommendation using AI.
    
    Analyzes user taste profile, current dislikes, restaurant menu, reviews,
    and community data to suggest the best food item with detailed reasoning.
    
    Args:
        restaurant_id (str): Unique identifier for the restaurant
        request (RecommendationRequest): Current session dislikes and preferences
        current_user: Injected current user from JWT token
        
    Returns:
        RecommendationResponse: AI-generated recommendation with confidence score
        
    Raises:
        HTTPException: 500 if recommendation generation fails
    """
    
    try:
        # Gather all context for the recommendation
        context = await gather_recommendation_context(
            current_user.id, 
            restaurant_id, 
            request.curr_dislikes
        )
        
        # Generate recommendation using Claude
        claude_response = await claude_client.generate_food_recommendation(
            user_profile=context.user_profile,
            restaurant_items=context.restaurant_items,
            reviews=context.restaurant_reviews,
            community_favorites=context.top_community_items,
            current_dislikes=context.current_dislikes,
            restaurant_name=f"Restaurant {restaurant_id}"
        )
        
        # Convert Claude response to FoodItemRecommendation
        recommendation = FoodItemRecommendation(
            id=f"claude_rec_{uuid.uuid4()}",
            name=claude_response.get("recommended_item", "Chef's Special"),
            description="AI-recommended item based on your preferences",
            price=15.99,  # Default price - would come from menu data in real implementation
            category="AI Recommendation",
            ingredients=[],
            allergens=[],
            calories=300,
            reviews=[],
            reasoning=claude_response.get("reasoning", "Recommended by our AI based on your taste profile")
        )
        
        # Generate session ID for tracking
        session_id = str(uuid.uuid4())
        
        # Use confidence score from Claude response
        confidence_score = claude_response.get("confidence", 0.85)
        
        return RecommendationResponse(
            item=recommendation,
            confidence_score=confidence_score,
            session_id=session_id,
            alternatives=[]  # Could include backup recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}"
        )

@router.get("/{restaurant_id}/context",
            summary="Get Recommendation Context",
            description="Retrieve the data context used for generating recommendations (useful for debugging and understanding AI decisions)",
            response_description="Summary of user profile, restaurant data, and community insights used for recommendations",
            responses={
                200: {
                    "description": "Context retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "user_profile_summary": {
                                    "dietary_restrictions": [],
                                    "cuisine_preferences": [{"cuisine_type": "Japanese", "preference_level": 5}],
                                    "flavor_profile": {
                                        "spicy_tolerance": 4,
                                        "umami_preference": 5,
                                        "sweet_preference": 3
                                    }
                                },
                                "available_items_count": 25,
                                "reviews_count": 127,
                                "community_favorites_count": 8
                            }
                        }
                    }
                }
            })
async def get_recommendation_context(
    restaurant_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the data context used for generating recommendations.
    
    Useful for debugging and understanding how the AI makes decisions.
    Shows user profile summary, available menu items, reviews, and community data.
    
    Args:
        restaurant_id (str): Unique identifier for the restaurant
        current_user: Injected current user from JWT token
        
    Returns:
        dict: Summary of recommendation context data
    """
    
    context = await gather_recommendation_context(
        current_user.id,
        restaurant_id,
        []
    )
    
    return {
        "user_profile_summary": context.user_profile,
        "available_items_count": len(context.restaurant_items),
        "reviews_count": len(context.restaurant_reviews),
        "community_favorites_count": len(context.top_community_items)
    }
