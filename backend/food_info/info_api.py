from fastapi import APIRouter, Depends
from .doordash.doordash_api import router as doordash_router
from .google_maps.gmaps_api import router as gmaps_router
from .beli.beli_api import router as beli_router
from .doordash.types.doordash_types import NearbyRestaurantsRequest, NearbyRestaurantsResponse, RestaurantMenu
from .google_maps.types.gmaps_types import RestaurantReviews
from .beli.types.beli_types import BeliRestaurantTopItems
from auth.auth_api import get_current_user
from auth.types.auth_types import UserResponse
from typing import List, Optional

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

router.include_router(doordash_router)
router.include_router(gmaps_router)
router.include_router(beli_router)

@router.post("/", response_model=NearbyRestaurantsResponse)
async def get_nearby_restaurants(
    request: NearbyRestaurantsRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get nearby restaurants (proxies to DoorDash API)"""
    # This will call the doordash endpoint
    from .doordash.doordash_api import get_nearby_restaurants as doordash_nearby
    return await doordash_nearby(request)

@router.get("/{restaurant_id}/items", response_model=RestaurantMenu)
async def get_restaurant_items(
    restaurant_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get restaurant menu items (proxies to DoorDash API)"""
    from .doordash.doordash_api import get_restaurant_menu
    return await get_restaurant_menu(restaurant_id)

@router.get("/{restaurant_id}/reviews", response_model=RestaurantReviews)
async def get_restaurant_reviews(
    restaurant_id: str,
    limit: Optional[int] = 10,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get restaurant reviews (proxies to Google Maps API)"""
    from .google_maps.gmaps_api import get_restaurant_reviews as gmaps_reviews
    return await gmaps_reviews(restaurant_id, limit)

@router.get("/{restaurant_id}/top_items", response_model=BeliRestaurantTopItems)
async def get_restaurant_top_items(
    restaurant_id: str,
    limit: Optional[int] = 10,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get top items from Beli (proxies to Beli API)"""
    from .beli.beli_api import get_restaurant_top_items
    return await get_restaurant_top_items(restaurant_id, limit, current_user)