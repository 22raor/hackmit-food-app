from typing import List, Optional
from pydantic import BaseModel


class OtherInfo(BaseModel):
    description: Optional[str] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None


class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[str] = None   # stored as string since you slice `[1:]`
    image_url: Optional[str] = None
    category: str
    rating: Optional[str] = None
    most_ordered: bool = False

class BeliTopItem(BaseModel):
    name: str
    image: str
    position: int


class RestaurantInfo(BaseModel):
    id: str                     # 6-digit string
    name: str
    average_rating: Optional[float] = None
    review_count: Optional[str] = None  # e.g. "(123+)"
    image_url: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: str
    state: str
    price_range: str
    tags: List[str] = []
    other_info: OtherInfo
    menu_items: List[MenuItem] = []
    place_id: str = ""
    reviews: List[str] = []
    beli_id: str = ''
    top_items: List[BeliTopItem] = []
