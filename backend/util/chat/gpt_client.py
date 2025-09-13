import openai
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

class GPTClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GPT client with API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        
    async def generate_food_recommendation(
        self,
        user_profile: Dict[str, Any],
        restaurant_items: List[Dict[str, Any]],
        reviews: List[Dict[str, Any]],
        community_favorites: List[Dict[str, Any]],
        current_dislikes: List[str],
        restaurant_name: str
    ) -> Dict[str, Any]:
        """Generate food recommendation using GPT"""
        
        # Build the prompt
        prompt = self._build_recommendation_prompt(
            user_profile=user_profile,
            restaurant_items=restaurant_items,
            reviews=reviews,
            community_favorites=community_favorites,
            current_dislikes=current_dislikes,
            restaurant_name=restaurant_name
        )
        
        try:
            # Mock response for now - replace with actual OpenAI call
            if not self.api_key:
                return self._mock_gpt_response(restaurant_items, current_dislikes)
            
            # Actual OpenAI API call (uncomment when ready to use)
            # response = await openai.ChatCompletion.acreate(
            #     model="gpt-4",
            #     messages=[
            #         {"role": "system", "content": "You are a food recommendation expert."},
            #         {"role": "user", "content": prompt}
            #     ],
            #     max_tokens=500,
            #     temperature=0.7
            # )
            # 
            # return self._parse_gpt_response(response.choices[0].message.content)
            
            return self._mock_gpt_response(restaurant_items, current_dislikes)
            
        except Exception as e:
            print(f"GPT API error: {e}")
            return self._mock_gpt_response(restaurant_items, current_dislikes)
    
    def _build_recommendation_prompt(
        self,
        user_profile: Dict[str, Any],
        restaurant_items: List[Dict[str, Any]],
        reviews: List[Dict[str, Any]],
        community_favorites: List[Dict[str, Any]],
        current_dislikes: List[str],
        restaurant_name: str
    ) -> str:
        """Build the GPT prompt for food recommendation"""
        
        prompt = f"""
You are a food recommendation expert helping a user choose their next meal at {restaurant_name}.

USER PROFILE:
- Dietary restrictions: {user_profile.get('dietary_restrictions', [])}
- Cuisine preferences: {user_profile.get('cuisine_preferences', [])}
- Flavor profile: {user_profile.get('flavor_profile', {})}
- Liked foods: {user_profile.get('liked_foods', [])}
- Disliked foods: {user_profile.get('disliked_foods', [])}

RESTAURANT MENU ITEMS:
{self._format_menu_items(restaurant_items)}

CUSTOMER REVIEWS:
{self._format_reviews(reviews)}

COMMUNITY FAVORITES:
{self._format_community_favorites(community_favorites)}

ITEMS USER HAS ALREADY REJECTED THIS SESSION:
{', '.join(current_dislikes) if current_dislikes else 'None'}

Please recommend ONE menu item that would be perfect for this user. Respond in JSON format:
{{
    "recommended_item": "exact menu item name",
    "reasoning": "detailed explanation of why this item matches the user's preferences",
    "confidence": 0.85
}}

Make sure to:
1. Avoid items the user has already rejected
2. Consider their dietary restrictions and preferences
3. Factor in positive reviews and community favorites
4. Provide a compelling reason for your recommendation
"""
        return prompt
    
    def _format_menu_items(self, items: List[Dict[str, Any]]) -> str:
        """Format menu items for the prompt"""
        formatted = []
        for item in items:
            formatted.append(f"- {item.get('name', 'Unknown')}: {item.get('description', '')} (${item.get('price', 0)})")
        return '\n'.join(formatted)
    
    def _format_reviews(self, reviews: List[Dict[str, Any]]) -> str:
        """Format reviews for the prompt"""
        formatted = []
        for review in reviews[:5]:  # Limit to top 5 reviews
            formatted.append(f"- {review.get('rating', 0)}/5 stars: {review.get('text', '')}")
        return '\n'.join(formatted)
    
    def _format_community_favorites(self, favorites: List[Dict[str, Any]]) -> str:
        """Format community favorites for the prompt"""
        formatted = []
        for fav in favorites:
            formatted.append(f"- {fav.get('name', 'Unknown')}: {fav.get('friend_recommendations', 0)} friend recommendations")
        return '\n'.join(formatted)
    
    def _mock_gpt_response(self, restaurant_items: List[Dict[str, Any]], current_dislikes: List[str]) -> Dict[str, Any]:
        """Mock GPT response for testing"""
        available_items = [item for item in restaurant_items if item.get('name') not in current_dislikes]
        
        if available_items:
            selected = available_items[0]
            return {
                "recommended_item": selected.get('name', 'Chef Special'),
                "reasoning": f"Based on your taste preferences, {selected.get('name', 'this item')} offers the perfect balance of flavors you enjoy. The fresh ingredients and expert preparation make it a standout choice.",
                "confidence": 0.85
            }
        else:
            return {
                "recommended_item": "Chef's Special",
                "reasoning": "Given your refined palate and the items you've explored, I recommend trying the chef's special - it represents the restaurant's creativity and expertise.",
                "confidence": 0.75
            }
    
    def _parse_gpt_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GPT response text into structured data"""
        try:
            import json
            return json.loads(response_text)
        except:
            # Fallback parsing if JSON parsing fails
            return {
                "recommended_item": "Chef's Special",
                "reasoning": response_text,
                "confidence": 0.7
            }
