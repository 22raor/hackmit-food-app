from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from auth.auth_api import router as auth_router
from user_profile.profile_api import router as profile_router
from food_info.info_api import router as restaurants_router
from recommender.recs_api import router as recs_router
import uvicorn

app = FastAPI(
    title="Food Recommender API",
    description="A Tinder-style food recommendation app with GPT-powered suggestions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Food Recommender API is running",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Food Recommender API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(restaurants_router)
app.include_router(recs_router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    uvicorn.run(
        "api_router:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )