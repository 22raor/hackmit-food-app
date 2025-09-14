from fastapi import APIRouter, Depends, HTTPException
from .doordash.doordash_api import router as doordash_router
from .google_maps.gmaps_api import router as gmaps_router
from .beli.beli_api import router as beli_router
from .doordash.types.doordash_types import NearbyRestaurantsRequest, NearbyRestaurantsResponse, RestaurantMenu
from .google_maps.types.gmaps_types import RestaurantReviews
from .beli.types.beli_types import BeliRestaurantTopItems
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from typing import List, Optional, Dict, Any
import json
import os
import glob

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

router.include_router(doordash_router)
router.include_router(gmaps_router)
router.include_router(beli_router)

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
            with open(file_path, 'r', encoding='utf-8') as f:
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
                        "beli_id": data.get("beli_id")
                    }
                    restaurants_list.append(restaurant_summary)

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    RESTAURANTS_CACHE = restaurants_dict
    RESTAURANTS_LIST_CACHE = restaurants_list
    print(f"Loaded {len(restaurants_dict)} restaurants into memory")

# Load restaurants on module import
load_all_restaurants_on_startup()



@router.get("/",
           summary="Get Restaurant List",
           description="Get a list of restaurants from in-memory cache",
           response_description="List of restaurants with basic information")
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
            "zip_code": "02101"
        }
    }

@router.post("/",
             response_model=NearbyRestaurantsResponse,
             summary="Get Nearby Restaurants",
             description="Find restaurants near a specific location using DoorDash data",
             response_description="List of nearby restaurants with basic information",
             responses={
                 200: {
                     "description": "Restaurants found successfully",
                     "content": {
                         "application/json": {
                             "example": {
                                 "restaurants": [
                                     {
                                         "id": "restaurant_123",
                                         "name": "Tony's Pizza",
                                         "address": "123 Main St, City, State",
                                         "phone": "+1-555-0123",
                                         "rating": 4.5,
                                         "cuisine_tags": ["italian", "pizza"],
                                         "image_url": "https://example.com/restaurant.jpg",
                                         "distance_miles": 0.8
                                     }
                                 ],
                                 "total_count": 25,
                                 "search_radius_miles": 5.0
                             }
                         }
                     }
                 }
             })
async def get_nearby_restaurants(
    request: NearbyRestaurantsRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Find restaurants near a specific location.

    Uses DoorDash API to search for restaurants within the specified radius
    of the given coordinates.

    Args:
        request (NearbyRestaurantsRequest): Search parameters including location and radius
        current_user: Injected current user from JWT token

    Returns:
        NearbyRestaurantsResponse: List of nearby restaurants with details
    """
    # This will call the doordash endpoint
    from .doordash.doordash_api import get_nearby_restaurants as doordash_nearby
    return await doordash_nearby(request)

def get_restaurant_by_id(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Get restaurant data by ID from in-memory cache"""
    return RESTAURANTS_CACHE.get(restaurant_id)

@router.get("/{restaurant_id}/items",
            summary="Get Restaurant Data",
            description="Retrieve complete restaurant data including menu items for a specific restaurant",
            response_description="Complete restaurant data with menu items",
            responses={
                200: {
                    "description": "Restaurant data retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "id": "58134",
                                "name": "Giggling Rice Thai",
                                "average_rating": 4.7,
                                "menu_items": [],
                                "reviews": [],
                                "top_items": []
                            }
                        }
                    }
                },
                404: {
                    "description": "Restaurant not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Restaurant not found"}
                        }
                    }
                }
            })
async def get_restaurant_items(
    restaurant_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve complete restaurant data for a specific restaurant.

    Gets all restaurant information including menu items, reviews, and top items.

    Args:
        restaurant_id (str): Unique identifier for the restaurant
        current_user: Injected current user from JWT token

    Returns:
        dict: Complete restaurant data

    Raises:
        HTTPException: 404 if restaurant not found
    """
    restaurant_data = get_restaurant_by_id(restaurant_id)

    if not restaurant_data:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return restaurant_data
