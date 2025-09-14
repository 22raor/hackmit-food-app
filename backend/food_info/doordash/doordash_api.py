from fastapi import APIRouter, HTTPException, status
from .types.doordash_types import (
    NearbyRestaurantsRequest,
    NearbyRestaurantsResponse,
    Restaurant,
    RestaurantMenu,
    MenuItem,
    RestaurantLocation,
)
from datetime import datetime
from typing import List

router = APIRouter(prefix="/doordash", tags=["doordash"])

MOCK_RESTAURANTS = [
    Restaurant(
        id="rest_1",
        name="Sakura Sushi",
        cuisine_tags=["Japanese", "Sushi", "Asian"],
        location=RestaurantLocation(
            latitude=42.3601,
            longitude=-71.0589,
            address="123 Main St",
            city="Boston",
            state="MA",
            zip_code="02101",
        ),
        rating=4.5,
        price_range="$$",
        image_url="https://example.com/sakura.jpg",
    ),
    Restaurant(
        id="rest_2",
        name="Tony's Pizza",
        cuisine_tags=["Italian", "Pizza", "Casual Dining"],
        location=RestaurantLocation(
            latitude=42.3615,
            longitude=-71.0570,
            address="456 Oak Ave",
            city="Boston",
            state="MA",
            zip_code="02101",
        ),
        rating=4.2,
        price_range="$",
        image_url="https://example.com/tonys.jpg",
    ),
]

MOCK_MENUS = {
    "rest_1": RestaurantMenu(
        restaurant_id="rest_1",
        restaurant_name="Sakura Sushi",
        items=[
            MenuItem(
                id="item_1",
                name="Dragon Roll",
                description="Shrimp tempura roll topped with avocado and eel sauce",
                price=14.99,
                category="Sushi Rolls",
                image_url="https://example.com/dragon-roll.jpg",
            ),
            MenuItem(
                id="item_2",
                name="Miso Soup",
                description="Traditional Japanese soup with tofu and seaweed",
                price=3.99,
                category="Appetizers",
            ),
            MenuItem(
                id="item_5",
                name="Salmon Sashimi",
                description="Fresh salmon sashimi, 6 pieces",
                price=12.99,
                category="Sashimi",
                image_url="https://example.com/salmon-sashimi.jpg",
            ),
        ],
    ),
    "rest_2": RestaurantMenu(
        restaurant_id="rest_2",
        restaurant_name="Tony's Pizza",
        items=[
            MenuItem(
                id="item_3",
                name="Margherita Pizza",
                description="Classic pizza with fresh mozzarella, tomato sauce, and basil",
                price=16.99,
                category="Pizza",
                image_url="https://example.com/margherita.jpg",
            ),
            MenuItem(
                id="item_4",
                name="Caesar Salad",
                description="Crisp romaine lettuce with parmesan and croutons",
                price=8.99,
                category="Appetizers",
            ),
            MenuItem(
                id="item_6",
                name="Pepperoni Pizza",
                description="Classic pepperoni pizza with mozzarella cheese",
                price=18.99,
                category="Pizza",
                image_url="https://example.com/pepperoni.jpg",
            ),
        ],
    ),
}


@router.post("/nearby", response_model=NearbyRestaurantsResponse)
async def get_nearby_restaurants(request: NearbyRestaurantsRequest):
    """Get nearby restaurants from DoorDash API"""
    # Mock implementation - replace with actual DoorDash API call
    filtered_restaurants = MOCK_RESTAURANTS.copy()

    # Apply limit
    if request.limit:
        filtered_restaurants = filtered_restaurants[: request.limit]

    return NearbyRestaurantsResponse(
        restaurants=filtered_restaurants,
        total_count=len(filtered_restaurants),
        search_location=RestaurantLocation(
            latitude=request.latitude,
            longitude=request.longitude,
            address="Search Location",
            city="Boston",
            state="MA",
            zip_code="02101",
        ),
    )


@router.get("/restaurant/{restaurant_id}/menu", response_model=RestaurantMenu)
async def get_restaurant_menu(restaurant_id: str):
    """Get restaurant menu from DoorDash API"""
    menu = MOCK_MENUS.get(restaurant_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu not found for restaurant {restaurant_id}",
        )

    return menu


@router.get("/restaurant/{restaurant_id}", response_model=Restaurant)
async def get_restaurant_details(restaurant_id: str):
    """Get restaurant details from DoorDash API"""
    restaurant = next((r for r in MOCK_RESTAURANTS if r.id == restaurant_id), None)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant {restaurant_id} not found",
        )

    return restaurant
