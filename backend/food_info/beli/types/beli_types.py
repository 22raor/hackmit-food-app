from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BeliTopItem(BaseModel):
    name: str
    photo_url: Optional[str] = None
    recommendation_count: int  # number of people who recommended it

class BeliRestaurantTopItems(BaseModel):
    restaurant_id: str
    restaurant_name: str
    top_items: List[BeliTopItem]
    last_updated: datetime

class BeliUserRestaurantReview(BaseModel):
    restaurant_name: str
    restaurant_id: Optional[str] = None
    rating: int  # numerical rating
    notes: Optional[str] = None  # optional notes about the restaurant
    date_reviewed: Optional[datetime] = None

class BeliUserProfile(BaseModel):
    user_id: str
    username: str
    restaurant_reviews: List[BeliUserRestaurantReview]
    total_reviews: int
    last_updated: datetime
