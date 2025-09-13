from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Review(BaseModel):
    id: str
    author_name: str
    author_url: Optional[str] = None
    language: str
    profile_photo_url: Optional[str] = None
    rating: int  # 1-5 stars
    relative_time_description: str
    text: str
    time: datetime

class PlaceDetails(BaseModel):
    place_id: str
    name: str
    formatted_address: str
    formatted_phone_number: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = None  # 0-4 scale
    opening_hours: Optional[List[str]] = None
    photos: List[str] = []

class RestaurantReviews(BaseModel):
    restaurant_id: str
    place_id: str
    restaurant_name: str
    overall_rating: Optional[float] = None
    total_reviews: int
    reviews: List[Review]
    last_updated: datetime

class MenuItemReviews(BaseModel):
    item_name: str
    restaurant_id: str
    reviews: List[Review]
    average_rating: Optional[float] = None
    mention_count: int
