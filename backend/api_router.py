from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth.auth_api import router as auth_router
from user_profile.profile_api import router as profile_router
from food_info.info_api import router as food_info_router
from recommender.recs_api import router as recommender_router
from config import settings
import uvicorn

app = FastAPI(
    title="Food Recommender API",
    description="""
    ## 🍔 Food Recommender API
    
    A Tinder-style food recommendation app that helps users discover food items by swiping through restaurant menus with Claude Haiku 3 AI-powered personalized suggestions.
    
    ### Key Features:
    - **Google OAuth Authentication**: Secure login with Google accounts
    - **Restaurant Discovery**: Browse restaurants via DoorDash, Google Maps, and Beli integrations
    - **Personalized Recommendations**: Claude Haiku 3 AI-powered food suggestions based on user preferences and taste profiles
    - **User Profiles**: Manage dietary preferences, allergies, and taste profiles
    - **Swipe Interface**: Tinder-style interface for discovering food items
    
    ### Authentication:
    1. Use `/auth/google` endpoint with Google ID token to authenticate
    2. Include the returned JWT token in the `Authorization` header as `Bearer <token>` for all authenticated requests
    
    ### API Structure:
    - **Auth**: `/auth/*` - Authentication and user management
    - **User Profile**: `/user_profile/*` - User preferences and taste profiles
    - **Restaurants**: `/restaurants/*` - Restaurant and menu data from multiple sources
    - **Recommendations**: `/recs/*` - AI-powered food recommendations
    
    ### External Integrations:
    - **DoorDash**: Restaurant listings and menus
    - **Google Maps**: Restaurant reviews and place details
    - **Beli**: Community recommendations and top items
    - **Claude Haiku 3**: Personalized recommendation engine
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Food Recommender Team",
        "email": "support@foodrecommender.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.foodrecommender.com",
            "description": "Production server"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS != ["*"] else ["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", 
         summary="Health Check",
         description="Check if the API is running and healthy",
         response_description="API health status",
         tags=["System"])
async def health_check():
    """
    Health check endpoint to verify API availability.
    
    Returns:
        dict: API status, message, and version information
    """
    return {
        "status": "healthy",
        "message": "Food Recommender API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/", 
         summary="API Information",
         description="Get basic information about the Food Recommender API",
         response_description="API welcome message and navigation links",
         tags=["System"])
async def root():
    """
    Root endpoint providing API information and navigation links.
    
    Returns:
        dict: Welcome message, documentation links, and version info
    """
    return {
        "message": "Welcome to the Food Recommender API",
        "description": "A Tinder-style food recommendation app with AI-powered suggestions",
        "docs": "/docs",
        "redoc": "/redoc", 
        "health": "/health",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "user_profile": "/user_profile", 
            "restaurants": "/restaurants",
            "recommendations": "/recs"
        }
    }

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(food_info_router)
app.include_router(recommender_router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    from fastapi import status
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    uvicorn.run(
        "api_router:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )