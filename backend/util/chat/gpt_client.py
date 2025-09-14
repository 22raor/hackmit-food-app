import anthropic
from typing import List, Dict, Any, Optional
import os
import json


class ClaudeClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        # print(self.api_key)
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            # print("client on init", self.client)
        else:
            self.client = None

    async def generate_food_recommendation(
        self,
        user_profile: Dict[str, Any],
        restaurant_items: List[Dict[str, Any]],
        reviews: List[str],
        community_favorites: List[Dict[str, Any]],
        current_dislikes: List[str],
        restaurant_name: str,
    ) -> Dict[str, Any]:
        """Generate food recommendation using Claude Haiku 3"""

        # Build the prompt
        prompt = self._build_recommendation_prompt(
            user_profile,
            restaurant_items,
            reviews,
            community_favorites,
            current_dislikes,
            restaurant_name,
        )
        try:
            # Mock response if no API key
            print("client on call", self.client)
            if self.client == None:
                print("MOCKED API RESPONSE")
                return self._mock_claude_response(restaurant_items, current_dislikes)

            # Actual Claude API call
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=5000,
                temperature=0.7,
                system=prompt,
                messages=[{"role": "user", "content": "generate next recommendation"}],
            )

            print("received api response")

            res = self._parse_claude_response(response.content[0].text)
            print(res)
            return res

        except Exception as e:
            import traceback

            # Format the traceback as a string
            tb_str = traceback.format_exc()
            print(f"Claude API error: {e}\nTraceback:\n{tb_str}")
            # print(f"Claude API error: {e.with_traceback(TracebackType)}")
            return self._mock_claude_response(restaurant_items, current_dislikes)

    def _build_recommendation_prompt(
        self,
        user_profile: Dict[str, Any],
        restaurant_items: List[Dict[str, Any]],
        reviews: List[str],
        community_favorites: List[Dict[str, Any]],
        current_dislikes: List[str],
        restaurant_name: str,
    ) -> str:
        """Build the Claude prompt for food recommendation"""

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
    "confidence": 0.85,
    "id": "menu_item_id"
}}

Make sure to:
1. Avoid items the user has already rejected
2. Consider their dietary restrictions and preferences
3. Factor in positive reviews and community favorites
4. Provide a compelling reason for your recommendation
5. Use ALL available information to make the best recommendation, especially also factor in popularity and user feedback
"""
        return prompt

    def _format_menu_items(self, items: List[Dict[str, Any]]) -> str:
        """Format menu items for the prompt"""
        formatted = []
        for i, item in enumerate(items):
            formatted.append(
                f"- id: {i+1} name: {item.get('name', 'Unknown')} "
                f"description: {item.get('description', '')} "
                f"price: (${item.get('price', 0)}) "
                f"category: {item.get('category', 'Unknown')}"
            )
        return "\n".join(formatted)

    def _format_reviews(self, reviews: List[str]) -> str:
        """Format reviews for the prompt"""
        return "\n".join(reviews)

    def _format_community_favorites(self, favorites: List[Dict[str, Any]]) -> str:
        """Format community favorites for the prompt"""
        formatted = []
        for fav in favorites:
            formatted.append(f"- name: {fav.get('name', 'Unknown')}")
        return "\n".join(formatted)

    def _mock_claude_response(
        self, restaurant_items: List[Dict[str, Any]], current_dislikes: List[str]
    ) -> Dict[str, Any]:
        """Mock Claude response for testing"""
        available_items = [
            item
            for item in restaurant_items
            if item.get("name") not in current_dislikes
        ]

        if available_items:
            selected = available_items[0]
            return {
                "recommended_item": selected.get("name", "Chef Special"),
                "reasoning": (
                    f"MOCK MF Based on your taste preferences, {selected.get('name', 'this item')} "
                    "offers the perfect balance of flavors you enjoy. The fresh ingredients "
                    "and expert preparation make it a standout choice."
                ),
                "confidence": 0.85,
            }

        return {
            "recommended_item": "Chef's Special",
            "reasoning": (
                "u fuck this is MOCK Given your refined palate and the items you've explored, I recommend "
                "trying the chef's special - it represents the restaurant's creativity and expertise."
            ),
            "confidence": 0.75,
        }

    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude response text into structured data"""
        try:
            parsed = json.loads(response_text)
            # print(f"Successfully parsed Claude response: {parsed}")

            # Ensure we have the required fields
            result = {
                "recommended_item": parsed.get("recommended_item", "Chef's Special"),
                "reasoning": parsed.get("reasoning", "AI-generated recommendation"),
                "confidence": parsed.get("confidence", 0.7),
            }

            return result

        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw response text: {response_text}")
            return {
                "recommended_item": "Chef's Special",
                "reasoning": response_text,
                "confidence": 0.7,
            }
