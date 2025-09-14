from fastapi import APIRouter, Depends, HTTPException
from .doordash.doordash_api import router as doordash_router
from .google_maps.gmaps_api import router as gmaps_router
from .beli.beli_api import router as beli_router

from .google_maps.types.gmaps_types import RestaurantReviews
from .beli.types.beli_types import BeliRestaurantTopItems
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from typing import List, Optional, Dict, Any
import json
import os
import glob

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# router.include_router(doordash_router)
# router.include_router(gmaps_router)
# router.include_router(beli_router)

# In-memory restaurant data storage
RESTAURANTS_CACHE: Dict[str, Dict[str, Any]] = {}
RESTAURANTS_LIST_CACHE: List[Dict[str, Any]] = []


def load_all_restaurants_on_startup():
    """Load all restaurant data into memory on startup"""
    global RESTAURANTS_CACHE, RESTAURANTS_LIST_CACHE

    processed_dir = os.path.join(os.path.dirname(__file__), "processed")
    json_files = glob.glob(os.path.join(processed_dir, "*.json"))

    restaurants_list = []
    restaurants_dict = {}

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                restaurant_id = data.get("id")

                if restaurant_id:
                    # Store full data in cache
                    restaurants_dict[restaurant_id] = data

                    # Create summary for list endpoint
                    restaurant_summary = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "average_rating": data.get("average_rating"),
                        "review_count": data.get("review_count"),
                        "image_url": data.get("image_url"),
                        "address": data.get("address"),
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "city": data.get("city"),
                        "state": data.get("state"),
                        "price_range": data.get("price_range"),
                        "tags": data.get("tags", []),
                        "place_id": data.get("place_id"),
                        "beli_id": data.get("beli_id"),
                    }
                    restaurants_list.append(restaurant_summary)

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    RESTAURANTS_CACHE = restaurants_dict
    RESTAURANTS_LIST_CACHE = restaurants_list
    print(f"Loaded {len(restaurants_dict), len(restaurants_list)} restaurants into memory")
    print(restaurants_dict.keys())


# Load restaurants on module import
load_all_restaurants_on_startup()


@router.get(
    "/",
    summary="Get Restaurant List",
    description="Get a list of restaurants from in-memory cache",
    response_description="List of restaurants with basic information",
)
async def get_restaurants(current_user: UserResponse = Depends(get_current_user)):
    """Get a list of restaurants from in-memory cache"""
    return {
        "restaurants": RESTAURANTS_LIST_CACHE,
        "total_count": len(RESTAURANTS_LIST_CACHE),
        "search_location": {
            "latitude": 42.3601,
            "longitude": -71.0589,
            "address": "Boston, MA",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02101",
        },
    }

def get_restaurant_by_id(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Get restaurant data by ID from in-memory cache"""
    return RESTAURANTS_CACHE.get(restaurant_id)
