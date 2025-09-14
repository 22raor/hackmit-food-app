from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from .doordash.doordash_api import router as doordash_router
from .google_maps.gmaps_api import router as gmaps_router
from .beli.beli_api import router as beli_router
from .doordash.types.doordash_types import NearbyRestaurantsRequest, NearbyRestaurantsResponse, RestaurantMenu
from .google_maps.types.gmaps_types import RestaurantReviews
from .beli.types.beli_types import BeliRestaurantTopItems
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from typing import List, Optional, Dict, Any
import tempfile
import os
import sys
import traceback

# Add path for OCR imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ocr.lib import get_restaurant_data
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
                    data["menu_items"] = [{**itm,"item_id": i} for i,itm in enumerate(data.get("menu_items", []))]
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


@router.post("/upload-menu", 
            summary="Upload Menu Image and Create Restaurant",
            description="Upload a menu image along with restaurant details to extract menu items and create restaurant data",
            response_description="Created restaurant data with extracted menu items")
async def upload_menu_and_create_restaurant(
    image: UploadFile = File(..., description="Menu image file (PNG, JPG, JPEG)"),
    name: str = Form(..., description="Restaurant name"),
    latitude: float = Form(..., description="Restaurant latitude"),
    longitude: float = Form(..., description="Restaurant longitude"), 
    city: str = Form(..., description="Restaurant city"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Upload a menu image and restaurant details to extract menu items using OCR and create restaurant data.
    
    This endpoint:
    1. Accepts an uploaded menu image
    2. Uses OCR to extract menu items from the image
    3. Enriches data with Google Maps and Beli information
    4. Stores the complete restaurant data in the cache
    5. Returns the processed restaurant information
    
    Args:
        image: Menu image file (PNG, JPG, JPEG formats supported)
        name: Name of the restaurant
        latitude: Restaurant latitude coordinate
        longitude: Restaurant longitude coordinate
        city: City where the restaurant is located
        current_user: Authenticated user (from JWT token)
        
    Returns:
        Dict: Complete restaurant data including extracted menu items
        
    Raises:
        HTTPException: 400 if image format is invalid or processing fails
        HTTPException: 500 if OCR or data enrichment fails
    """
    
    # Validate image file type
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file.")
    
    # Create temporary file for the uploaded image
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            content = await image.read()
            temp_file.write(content)
            temp_image_path = temp_file.name
        
        # Process the restaurant data using OCR
        restaurant_data = get_restaurant_data(temp_image_path, name, latitude, longitude, city)
        
        # Convert RestaurantInfo object to dictionary for caching
        restaurant_dict = restaurant_data.dict()
        
        # Store in cache using the restaurant ID
        restaurant_id = restaurant_dict['google_id'] if restaurant_dict.get('google_id') else restaurant_dict['id']
        RESTAURANTS_CACHE[restaurant_id] = restaurant_dict
        
        data = restaurant_dict
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
        # restaurants_list.append(restaurant_summary)
        
        # Also add to the list cache
        if restaurant_summary not in RESTAURANTS_LIST_CACHE:
            RESTAURANTS_LIST_CACHE.append(restaurant_summary)
        
        return {
            "success": True,
            "message": f"Restaurant '{name}' processed and cached successfully",
            "restaurant_id": restaurant_id,
            "restaurant_data": restaurant_dict
        }
        
    except Exception as e:
        error_detail = {
            "message": "Failed to process restaurant data",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)
    finally:
        # Clean up temporary file
        if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
            os.unlink(temp_image_path)


