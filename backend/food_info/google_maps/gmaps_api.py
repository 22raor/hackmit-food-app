from fastapi import APIRouter, HTTPException, status
from .types.gmaps_types import RestaurantReviews, MenuItemReviews, Review, PlaceDetails
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/google_maps", tags=["google_maps"])

# Mock data - replace with actual Google Maps API calls later
MOCK_REVIEWS = {
    "rest_1": RestaurantReviews(
        restaurant_id="rest_1",
        place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
        restaurant_name="Sakura Sushi",
        overall_rating=4.5,
        total_reviews=127,
        reviews=[
            Review(
                id="review_1",
                author_name="John D.",
                language="en",
                rating=5,
                relative_time_description="2 weeks ago",
                text="Amazing sushi! The Dragon Roll was absolutely delicious. Fresh ingredients and great presentation.",
                time=datetime.utcnow(),
            ),
            Review(
                id="review_2",
                author_name="Sarah M.",
                language="en",
                rating=4,
                relative_time_description="1 month ago",
                text="Good quality sushi, though a bit pricey. The miso soup was excellent.",
                time=datetime.utcnow(),
            ),
        ],
        last_updated=datetime.utcnow(),
    ),
    "rest_2": RestaurantReviews(
        restaurant_id="rest_2",
        place_id="ChIJN1t_tDeuEmsRUsoyG83frY5",
        restaurant_name="Tony's Pizza",
        overall_rating=4.2,
        total_reviews=89,
        reviews=[
            Review(
                id="review_3",
                author_name="Mike R.",
                language="en",
                rating=5,
                relative_time_description="1 week ago",
                text="Best pizza in the area! The Margherita is perfect - crispy crust and fresh ingredients.",
                time=datetime.utcnow(),
            ),
            Review(
                id="review_4",
                author_name="Lisa K.",
                language="en",
                rating=3,
                relative_time_description="3 weeks ago",
                text="Decent pizza but service was slow. The Caesar salad was good though.",
                time=datetime.utcnow(),
            ),
        ],
        last_updated=datetime.utcnow(),
    ),
}

MOCK_ITEM_REVIEWS = {
    "Dragon Roll": MenuItemReviews(
        item_name="Dragon Roll",
        restaurant_id="rest_1",
        reviews=[
            Review(
                id="item_review_1",
                author_name="John D.",
                language="en",
                rating=5,
                relative_time_description="2 weeks ago",
                text="The Dragon Roll was absolutely delicious. Fresh ingredients and great presentation.",
                time=datetime.utcnow(),
            )
        ],
        average_rating=4.8,
        mention_count=15,
    ),
    "Margherita Pizza": MenuItemReviews(
        item_name="Margherita Pizza",
        restaurant_id="rest_2",
        reviews=[
            Review(
                id="item_review_2",
                author_name="Mike R.",
                language="en",
                rating=5,
                relative_time_description="1 week ago",
                text="The Margherita is perfect - crispy crust and fresh ingredients.",
                time=datetime.utcnow(),
            )
        ],
        average_rating=4.6,
        mention_count=23,
    ),
}


@router.get("/restaurant/{restaurant_id}/reviews", response_model=RestaurantReviews)
async def get_restaurant_reviews(restaurant_id: str, limit: Optional[int] = 10):
    """Get Google Maps reviews for a restaurant"""
    # Mock implementation - replace with actual Google Maps API call
    reviews = MOCK_REVIEWS.get(restaurant_id)
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reviews not found for restaurant {restaurant_id}",
        )

    # Apply limit to reviews
    if limit and len(reviews.reviews) > limit:
        limited_reviews = reviews.reviews[:limit]
        reviews.reviews = limited_reviews

    return reviews


@router.get(
    "/restaurant/{restaurant_id}/item/{item_name}/reviews",
    response_model=MenuItemReviews,
)
async def get_menu_item_reviews(restaurant_id: str, item_name: str):
    """Get reviews mentioning a specific menu item"""
    # Mock implementation - replace with actual Google Maps API call and text analysis
    item_reviews = MOCK_ITEM_REVIEWS.get(item_name)
    if not item_reviews:
        # Return empty reviews if no specific mentions found
        return MenuItemReviews(
            item_name=item_name,
            restaurant_id=restaurant_id,
            reviews=[],
            average_rating=None,
            mention_count=0,
        )

    return item_reviews


@router.get("/restaurant/{restaurant_id}/place_details", response_model=PlaceDetails)
async def get_place_details(restaurant_id: str):
    """Get detailed place information from Google Maps"""
    # Mock implementation - replace with actual Google Maps Places API call
    if restaurant_id == "rest_1":
        return PlaceDetails(
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
            name="Sakura Sushi",
            formatted_address="123 Main St, Boston, MA 02101, USA",
            formatted_phone_number="(617) 555-0123",
            website="https://sakurasushi.com",
            rating=4.5,
            user_ratings_total=127,
            price_level=2,
            opening_hours=[
                "Monday: 11:00 AM – 10:00 PM",
                "Tuesday: 11:00 AM – 10:00 PM",
                "Wednesday: 11:00 AM – 10:00 PM",
                "Thursday: 11:00 AM – 10:00 PM",
                "Friday: 11:00 AM – 11:00 PM",
                "Saturday: 11:00 AM – 11:00 PM",
                "Sunday: 12:00 PM – 9:00 PM",
            ],
            photos=["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"],
        )
    elif restaurant_id == "rest_2":
        return PlaceDetails(
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY5",
            name="Tony's Pizza",
            formatted_address="456 Oak Ave, Boston, MA 02101, USA",
            formatted_phone_number="(617) 555-0456",
            website="https://tonyspizza.com",
            rating=4.2,
            user_ratings_total=89,
            price_level=1,
            opening_hours=[
                "Monday: 10:00 AM – 11:00 PM",
                "Tuesday: 10:00 AM – 11:00 PM",
                "Wednesday: 10:00 AM – 11:00 PM",
                "Thursday: 10:00 AM – 11:00 PM",
                "Friday: 10:00 AM – 12:00 AM",
                "Saturday: 10:00 AM – 12:00 AM",
                "Sunday: 11:00 AM – 10:00 PM",
            ],
            photos=["https://example.com/pizza1.jpg", "https://example.com/pizza2.jpg"],
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place details not found for restaurant {restaurant_id}",
        )
