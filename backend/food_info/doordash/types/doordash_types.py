from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class RestaurantLocation(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    zip_code: str

class Restaurant(BaseModel):
    id: str
    name: str
    cuisine_tags: List[str] = []
    location: RestaurantLocation
    rating: Optional[float] = None
    price_range: str
    image_url: Optional[str] = None

class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None

class RestaurantMenu(BaseModel):
    restaurant_id: str
    restaurant_name: str
    items: List[MenuItem]

class NearbyRestaurantsRequest(BaseModel):
    latitude: float
    longitude: float
    radius_miles: Optional[float] = 5.0
    limit: Optional[int] = 20

class NearbyRestaurantsResponse(BaseModel):
    restaurants: List[Restaurant]
    total_count: int
    search_location: RestaurantLocation
