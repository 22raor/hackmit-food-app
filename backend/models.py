"""
SQLAlchemy models for the Food Recommender API
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    google_id = Column(String, unique=True, index=True, nullable=False)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to taste profile
    taste_profile = relationship("TasteProfile", back_populates="user", uselist=False)

class TasteProfile(Base):
    __tablename__ = "taste_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Dietary preferences
    dietary_restrictions = Column(JSON, default=list)  # ["vegetarian", "gluten_free", etc.]
    allergies = Column(JSON, default=list)  # ["nuts", "dairy", etc.]

    # Cuisine preferences
    preferred_cuisines = Column(JSON, default=list)  # ["italian", "mexican", etc.]
    disliked_cuisines = Column(JSON, default=list)

    # Spice and flavor preferences
    spice_tolerance = Column(String, default="medium")  # "mild", "medium", "hot"
    flavor_preferences = Column(JSON, default=list)  # ["sweet", "savory", "umami", etc.]

    # Price and health preferences
    price_range = Column(String, default="medium")  # "low", "medium", "high"
    health_consciousness = Column(String, default="medium")  # "low", "medium", "high"

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="taste_profile")

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String, primary_key=True)  # External ID from DoorDash/Google Maps
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    cuisine_type = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    price_range = Column(String, nullable=True)  # "$", "$$", "$$$", "$$$$"
    image_url = Column(String, nullable=True)

    # Location data
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # External service data
    doordash_id = Column(String, nullable=True)
    google_place_id = Column(String, nullable=True)
    beli_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    # Nutritional info
    calories = Column(Integer, nullable=True)
    ingredients = Column(JSON, default=list)
    allergens = Column(JSON, default=list)

    # External service data
    doordash_item_id = Column(String, nullable=True)
    beli_item_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    restaurant = relationship("Restaurant")

class UserSwipe(Base):
    __tablename__ = "user_swipes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(String, ForeignKey("menu_items.id"), nullable=False)

    # Swipe data
    swiped_right = Column(Boolean, nullable=False)  # True = like, False = dislike
    session_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    menu_item = relationship("MenuItem")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(String, ForeignKey("menu_items.id"), nullable=False)

    # Recommendation data
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    session_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    menu_item = relationship("MenuItem")
