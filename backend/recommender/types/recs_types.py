from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class RecommendationRequest(BaseModel):
    curr_dislikes: List[str] = []


class FoodItemRecommendation(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    ingredients: List[str] = []
    allergens: List[str] = []
    calories: Optional[int] = None
    reviews: List[Dict[str, Any]] = []
    reasoning: str  # GPT's explanation for why this item was recommended


class RecommendationResponse(BaseModel):
    item: FoodItemRecommendation
    confidence_score: float  # 0-1 scale
    session_id: str
    alternatives: List[FoodItemRecommendation] = []


class RecommendationContext(BaseModel):
    user_profile: Dict[str, Any]
    restaurant_items: List[Dict[str, Any]]
    restaurant_reviews: List[str]
    top_community_items: List[Dict[str, Any]]
    current_dislikes: List[str]
    session_history: List[str] = []


class GPTPromptData(BaseModel):
    user_taste_profile: str
    restaurant_menu: str
    reviews_summary: str
    community_favorites: str
    current_dislikes: str
    prompt_template: str
