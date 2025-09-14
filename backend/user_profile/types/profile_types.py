from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class DietaryRestriction(BaseModel):
    name: str
    severity: str  # "allergy", "intolerance", "preference"


class CuisinePreference(BaseModel):
    cuisine_type: str
    preference_level: int  # 1-5 scale


class FlavorProfile(BaseModel):
    spicy_tolerance: int  # 1-5 scale
    sweet_preference: int  # 1-5 scale
    salty_preference: int  # 1-5 scale
    sour_preference: int  # 1-5 scale
    umami_preference: int  # 1-5 scale
    bitter_tolerance: int  # 1-5 scale


class FoodItem(BaseModel):
    name: str
    restaurant: Optional[str] = None
    cuisine_type: Optional[str] = None
    tags: List[str] = []


class UserTasteProfile(BaseModel):
    user_id: str
    dietary_restrictions: List[DietaryRestriction] = []
    cuisine_preferences: List[CuisinePreference] = []
    flavor_profile: Optional[FlavorProfile] = None
    liked_foods: List[FoodItem] = []
    disliked_foods: List[FoodItem] = []
    favorite_restaurants: List[str] = []
    price_range_preference: Optional[str] = None  # "budget", "mid-range", "upscale"
    meal_time_preferences: Dict[str, List[str]] = (
        {}
    )  # {"breakfast": ["light", "protein-rich"], ...}
    updated_at: datetime


class UpdateTasteProfile(BaseModel):
    dietary_restrictions: Optional[List[DietaryRestriction]] = None
    cuisine_preferences: Optional[List[CuisinePreference]] = None
    flavor_profile: Optional[FlavorProfile] = None
    liked_foods: Optional[List[FoodItem]] = None
    disliked_foods: Optional[List[FoodItem]] = None
    favorite_restaurants: Optional[List[str]] = None
    price_range_preference: Optional[str] = None
    meal_time_preferences: Optional[Dict[str, List[str]]] = None


class TasteProfileResponse(BaseModel):
    profile: UserTasteProfile
    recommendations_count: int
    last_activity: Optional[datetime] = None
