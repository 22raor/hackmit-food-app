#!/usr/bin/env python3
"""
API Tester for Food Recommender API

This script tests the complete flow:
1. Google OAuth authentication
2. User profile updates
3. Restaurant data retrieval
4. AI recommendations

Usage:
    python api_tester.py --google-id "your-google-id-token"
    python api_tester.py --mock-google-id "test@example.com"
"""

import asyncio
import httpx
import json
import argparse
import sys
from typing import Optional

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.jwt_token: Optional[str] = None
        self.user_id: Optional[str] = None
        
    def _get_headers(self) -> dict:
        """Get headers with JWT token if available"""
        headers = {"Content-Type": "application/json"}
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        return headers
    
    async def test_google_auth(self, google_id_token: str) -> bool:
        """Test Google OAuth authentication"""
        print("🔐 Testing Google OAuth authentication...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/auth/google",
                    json={"id_token": google_id_token},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.jwt_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("id")
                    
                    print(f"✅ Authentication successful!")
                    print(f"   User ID: {self.user_id}")
                    print(f"   JWT Token: {self.jwt_token[:20]}...")
                    print(f"   Is New User: {data.get('is_new_user', False)}")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Authentication error: {str(e)}")
                return False
    
    async def test_auth_me(self) -> bool:
        """Test /auth/me endpoint to verify JWT token"""
        print("\n👤 Testing /auth/me endpoint...")
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/auth/me",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Auth verification successful!")
                    print(f"   User: {data.get('name')} ({data.get('email')})")
                    return True
                else:
                    print(f"❌ Auth verification failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Auth verification error: {str(e)}")
                return False
    
    async def test_update_user_profile(self) -> bool:
        """Test updating user taste profile"""
        print("\n🍽️ Testing user profile update...")
        
        if not self.user_id:
            print("❌ No user ID available")
            return False
            
        profile_data = {
            "dietary_restrictions": ["vegetarian"],
            "cuisine_preferences": [
                {"cuisine_type": "Japanese", "preference_level": 5},
                {"cuisine_type": "Italian", "preference_level": 4}
            ],
            "flavor_profile": {
                "spicy_tolerance": 3,
                "umami_preference": 5,
                "sweet_preference": 2
            },
            "allergies": ["nuts"],
            "favorite_dishes": ["sushi", "ramen"]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/user_profile/{self.user_id}",
                    json=profile_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    print("✅ Profile update successful!")
                    print(f"   Updated dietary restrictions: {profile_data['dietary_restrictions']}")
                    print(f"   Updated cuisine preferences: {len(profile_data['cuisine_preferences'])} items")
                    return True
                else:
                    print(f"❌ Profile update failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Profile update error: {str(e)}")
                return False
    
    async def test_get_user_profile(self) -> bool:
        """Test getting user taste profile to verify changes"""
        print("\n📋 Testing user profile retrieval...")
        
        if not self.user_id:
            print("❌ No user ID available")
            return False
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user_profile/{self.user_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Profile retrieval successful!")
                    print(f"   Dietary restrictions: {data.get('dietary_restrictions', [])}")
                    print(f"   Cuisine preferences: {len(data.get('cuisine_preferences', []))} items")
                    print(f"   Spicy tolerance: {data.get('flavor_profile', {}).get('spicy_tolerance', 'N/A')}")
                    return True
                else:
                    print(f"❌ Profile retrieval failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Profile retrieval error: {str(e)}")
                return False
    
    async def test_get_restaurants(self) -> Optional[str]:
        """Test getting restaurant list and return a restaurant ID"""
        print("\n🏪 Testing restaurant list retrieval...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/restaurants",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    restaurants = data if isinstance(data, list) else data.get('restaurants', [])
                    
                    if restaurants:
                        restaurant_id = restaurants[0].get('id')
                        restaurant_name = restaurants[0].get('name', 'Unknown')
                        print(f"✅ Restaurant list retrieved successfully!")
                        print(f"   Found {len(restaurants)} restaurants")
                        print(f"   Using restaurant: {restaurant_name} (ID: {restaurant_id})")
                        return restaurant_id
                    else:
                        print("⚠️ No restaurants found in response")
                        return None
                else:
                    print(f"❌ Restaurant retrieval failed: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"❌ Restaurant retrieval error: {str(e)}")
                return None
    
    async def test_get_recommendation(self, restaurant_id: str) -> bool:
        """Test getting AI recommendation for a restaurant"""
        print(f"\n🤖 Testing AI recommendation for restaurant {restaurant_id}...")
        
        recommendation_data = {
            "current_dislikes": ["spicy food", "raw fish"]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/recs/{restaurant_id}",
                    json=recommendation_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    item = data.get('item', {})
                    print("✅ AI recommendation successful!")
                    print(f"   Recommended item: {item.get('name', 'Unknown')}")
                    print(f"   Description: {item.get('description', 'N/A')}")
                    print(f"   Price: ${item.get('price', 'N/A')}")
                    print(f"   Reasoning: {item.get('reasoning', 'N/A')[:100]}...")
                    return True
                else:
                    print(f"❌ Recommendation failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Recommendation error: {str(e)}")
                return False
    
    async def run_full_test(self, google_id_token: str) -> bool:
        """Run the complete test suite"""
        print("🚀 Starting Food Recommender API Test Suite")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not await self.test_google_auth(google_id_token):
            return False
        
        # Step 2: Verify authentication
        if not await self.test_auth_me():
            return False
        
        # Step 3: Update user profile
        if not await self.test_update_user_profile():
            return False
        
        # Step 4: Verify profile changes
        if not await self.test_get_user_profile():
            return False
        
        # Step 5: Get restaurants
        restaurant_id = await self.test_get_restaurants()
        if not restaurant_id:
            print("⚠️ Skipping recommendation test - no restaurant ID available")
            return True
        
        # Step 6: Get AI recommendation
        if not await self.test_get_recommendation(restaurant_id):
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        return True

async def main():
    parser = argparse.ArgumentParser(description="Test Food Recommender API")
    parser.add_argument("--google-id", help="Google OAuth ID token")
    parser.add_argument("--mock-google-id", help="Mock Google ID (email) for testing")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    # if not args.google_id and not args.mock_google_id:
    #     print("❌ Please provide either --google-id or --mock-google-id")
    #     sys.exit(1)
    
    # Use mock token if provided, otherwise use real Google ID token
    # google_token = 'mc..gDAMcrXIg_e9wEGLB5NWOzl5vDt9YlKHqniHUDbRdzlqV-yb96GHfjzxt96Zl7IcWNzgFdn7ZgROFSSU_s6FzOIJCjigeiL8raPr-wPvleNJbrd5qSaK9YZ6uEOtEGEM0LB_2LaObRGROjQNCG6yPDcHNe_MMbAkfj7nwgwuaT0Fv46qX5algMPf08t9rQss9rbBV2ZHGQX_j2ma8Dt43_ZTXt1IfGXv5SzA5T6k52ySXvdKqEWARsFZiI1EClCSPFV-oqbkzD5kuqqBTWxvKrkFbT4iNdgeF27yB_hhy0ZeXUBr1dolzGfpyJYiDLw3ZDd74ccoDsit-5AaWkvrpw'
    google_token = 'mock'

    tester = APITester(args.base_url)
    
    try:
        success = await tester.run_full_test(google_token)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
