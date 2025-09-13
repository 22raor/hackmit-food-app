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

@router.get("/{restaurant_id}/items", 
            response_model=RestaurantMenu,
            summary="Get Restaurant Menu",
            description="Retrieve the complete menu for a specific restaurant",
            response_description="Restaurant menu with all available items",
            responses={
                200: {
                    "description": "Menu retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "restaurant_id": "restaurant_123",
                                "restaurant_name": "Tony's Pizza",
                                "items": [
                                    {
                                        "id": "item_456",
                                        "name": "Margherita Pizza",
                                        "description": "Fresh mozzarella, tomato sauce, basil",
                                        "price": 18.99,
                                        "image_url": "https://example.com/pizza.jpg"
                                    }
                                ]
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
    Retrieve the complete menu for a specific restaurant.
    
    Gets all menu items available at the restaurant including names,
    descriptions, prices, and images.
    
    Args:
        restaurant_id (str): Unique identifier for the restaurant
        current_user: Injected current user from JWT token
        
    Returns:
        RestaurantMenu: Complete menu with all items
        
    Raises:
        HTTPException: 404 if restaurant not found
    """
    from .doordash.doordash_api import get_restaurant_menu
    return await get_restaurant_menu(restaurant_id)

@router.get("/{restaurant_id}/reviews", 
            response_model=RestaurantReviews,
            summary="Get Restaurant Reviews",
            description="Retrieve customer reviews for a specific restaurant from Google Maps",
            response_description="List of customer reviews with ratings and comments",
            responses={
                200: {
                    "description": "Reviews retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "restaurant_id": "restaurant_123",
                                "reviews": [
                                    {
                                        "id": "review_789",
                                        "author_name": "John D.",
                                        "rating": 5,
                                        "text": "Amazing pizza! Best in the city.",
                                        "time": "2024-01-01T12:00:00",
                                        "profile_photo_url": "https://example.com/profile.jpg"
                                    }
                                ],
                                "average_rating": 4.5,
                                "total_reviews": 127
                            }
                        }
                    }
                }
            })
async def get_restaurant_reviews(
    restaurant_id: str,
    limit: Optional[int] = 10,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve customer reviews for a specific restaurant.
    
    Gets reviews from Google Maps including ratings, comments, and reviewer information.
    
    Args:
        restaurant_id (str): Unique identifier for the restaurant
        limit (int, optional): Maximum number of reviews to return. Defaults to 10.
        current_user: Injected current user from JWT token
        
    Returns:
        RestaurantReviews: List of reviews with average rating and total count
    """
    from .google_maps.gmaps_api import get_restaurant_reviews as gmaps_reviews
    return await gmaps_reviews(restaurant_id, limit)

@router.get("/{restaurant_id}/top_items", 
            response_model=BeliRestaurantTopItems,
            summary="Get Restaurant Top Items",
            description="Retrieve the most recommended items for a restaurant from Beli community data",
            response_description="List of top recommended menu items with recommendation counts",
            responses={
                200: {
                    "description": "Top items retrieved successfully",
                    "content": {
                        "application/json": {
                            "example": {
                                "restaurant_id": "restaurant_123",
                                "restaurant_name": "Tony's Pizza",
                                "top_items": [
                                    {
                                        "name": "Margherita Pizza",
                                        "photo_url": "https://example.com/pizza.jpg",
                                        "recommendation_count": 45
                                    },
                                    {
                                        "name": "Caesar Salad",
                                        "photo_url": "https://example.com/salad.jpg",
                                        "recommendation_count": 32
                                    }
                                ]
                            }
                        }
                    }
                }
            })
async def get_restaurant_top_items(
    restaurant_id: str,
    limit: Optional[int] = 10,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Retrieve the most recommended items for a restaurant.
    
    Gets community-recommended items from Beli, showing which dishes
    are most popular and highly rated by other users.
    
    Args:
        restaurant_id (str): Unique identifier for the restaurant
        limit (int, optional): Maximum number of top items to return. Defaults to 10.
        current_user: Injected current user from JWT token
        
    Returns:
        BeliRestaurantTopItems: List of top recommended items with counts
    """
    from .beli.beli_api import get_restaurant_top_items
    return await get_restaurant_top_items(restaurant_id, limit, current_user)