# Hackmit Food App

**DEMO**: https://youtu.be/ulMwv87ibrg
**LOOM**: https://www.loom.com/share/f2f397ec5311411093bb33981657d099?sid=c8314676-5f2a-42f1-abf5-a30c9562e6b1

# Food Recommender API

A Tinder-style food recommendation app with GPT-powered suggestions that helps users discover their perfect meal through an intuitive swipe interface. We use a combination of vision LLMs, voice agents, web scraping, reverse engineering, and some APIs to work.

## 🍽️ Project Overview

This app provides personalized food recommendations by:
- **Authentication**: Secure user registration and login
- **Restaurant Discovery**: Finding nearby restaurants via DoorDash integration
- **Swipe Interface**: Tinder-like cards for food items
- **Smart Recommendations**: GPT-powered suggestions based on user preferences, reviews, and social proof
- **Taste Profiling**: Learning from user preferences and dietary restrictions

## 🏗️ Architecture

## 🚀 API Endpoints

### Authentication (`/auth`)
- `POST /auth/login` - User login with JWT token
- `GET /auth/me` - Get current user info

### User Profile (`/user_profile`)
- `GET /user_profile/{user_id}` - Get taste profile
- `POST /user_profile/{user_id}` - Update taste preferences

### Restaurants (`/restaurants`)
- `GET /restaurants/` - Find nearby restaurants

### Recommendations (`/recs`)
- `POST /recs/{restaurant_id}` - Get GPT recommendation for the next food item.
  ```json
  {
    "curr_dislikes": ["California Roll", "Miso Soup"]
  }
  ```

## 🔧 Setup & Installation

1. **Install dependencies**:
   `git clone git@github.com:22raor/hackmit-food-app.git`

2. **Environment variables** (create `.env` file):
   Fill out the .env.example file.

3. **Run the server**:
   Run `docker-compose build && docker-compose up`.

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🧠 How Recommendations Work

1. **Context Gathering**: Collect user taste profile, restaurant menu, reviews, and community data
2. **GPT Prompting**: Build structured prompt with all relevant information
3. **Smart Filtering**: Exclude previously rejected items and respect dietary restrictions
4. **Reasoning**: Provide clear explanation for each recommendation
5. **Stateless Design**: Each request includes current session dislikes

## 🔮 Current Status

✅ **Completed**:
- Complete API structure with all endpoints
- Authentication system with JWT
- User taste profile management
- Mock integrations for DoorDash, Google Maps, and Beli
- GPT recommendation engine framework
- Utility modules for fuzzy matching and prompt building

🚧 **Next Steps**:
- Add order placement functionality

## 🛠️ Development Notes

## 📱 Frontend Integration

The API is designed to support a mobile-first Tinder-style interface:
1. User selects restaurant from nearby list
2. App creates recommendation session
3. User swipes left (dislike) or right (like) on food cards
4. Each swipe updates `curr_dislikes` for next recommendation
5. Right swipe triggers order flow (future feature)

Run the server and visit `/docs` for interactive API documentation!
