from typing import Dict, List, Any, Optional
from datetime import datetime


class PromptBuilder:
    """Utility class for building structured prompts for GPT recommendations"""

    @staticmethod
    def build_recommendation_prompt(
        user_profile: Dict[str, Any],
        restaurant_name: str,
        menu_items: List[Dict[str, Any]],
        reviews: List[Dict[str, Any]],
        community_data: List[Dict[str, Any]],
        rejected_items: List[str],
        session_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build a comprehensive prompt for food recommendations"""

        prompt_sections = []

        # System context
        prompt_sections.append(
            f"You are an expert food recommendation AI helping a user choose their next meal at {restaurant_name}. "
            "Your goal is to recommend ONE perfect menu item based on their preferences, dietary needs, and social proof."
        )

        # User profile section
        user_section = PromptBuilder._build_user_profile_section(user_profile)
        prompt_sections.append(user_section)

        # Menu items section
        menu_section = PromptBuilder._build_menu_section(menu_items)
        prompt_sections.append(menu_section)

        # Reviews section
        if reviews:
            reviews_section = PromptBuilder._build_reviews_section(reviews)
            prompt_sections.append(reviews_section)

        # Community data section
        if community_data:
            community_section = PromptBuilder._build_community_section(community_data)
            prompt_sections.append(community_section)

        # Rejected items section
        if rejected_items:
            rejected_section = (
                f"\nITEMS ALREADY REJECTED THIS SESSION:\n{', '.join(rejected_items)}"
            )
            prompt_sections.append(rejected_section)

        # Response format instructions
        format_section = PromptBuilder._build_response_format_section()
        prompt_sections.append(format_section)

        return "\n\n".join(prompt_sections)

    @staticmethod
    def _build_user_profile_section(user_profile: Dict[str, Any]) -> str:
        """Build the user profile section of the prompt"""
        sections = ["USER PROFILE:"]

        # Dietary restrictions
        restrictions = user_profile.get("dietary_restrictions", [])
        if restrictions:
            restriction_names = [
                r.get("name", "") for r in restrictions if isinstance(r, dict)
            ]
            if not restriction_names:
                restriction_names = restrictions
            sections.append(f"- Dietary restrictions: {', '.join(restriction_names)}")

        # Cuisine preferences
        cuisines = user_profile.get("cuisine_preferences", [])
        if cuisines:
            cuisine_text = []
            for cuisine in cuisines:
                if isinstance(cuisine, dict):
                    name = cuisine.get("cuisine_type", "")
                    level = cuisine.get("preference_level", 0)
                    cuisine_text.append(f"{name} ({level}/5)")
                else:
                    cuisine_text.append(str(cuisine))
            sections.append(f"- Cuisine preferences: {', '.join(cuisine_text)}")

        # Flavor profile
        flavor_profile = user_profile.get("flavor_profile", {})
        if flavor_profile:
            flavor_text = []
            for flavor, level in flavor_profile.items():
                if isinstance(level, (int, float)):
                    flavor_text.append(f"{flavor.replace('_', ' ')}: {level}/5")
            if flavor_text:
                sections.append(f"- Flavor preferences: {', '.join(flavor_text)}")

        # Liked/disliked foods
        liked_foods = user_profile.get("liked_foods", [])
        if liked_foods:
            food_names = [
                f.get("name", f) if isinstance(f, dict) else str(f) for f in liked_foods
            ]
            sections.append(f"- Previously liked: {', '.join(food_names[:5])}")

        disliked_foods = user_profile.get("disliked_foods", [])
        if disliked_foods:
            food_names = [
                f.get("name", f) if isinstance(f, dict) else str(f)
                for f in disliked_foods
            ]
            sections.append(f"- Previously disliked: {', '.join(food_names[:5])}")

        return "\n".join(sections)

    @staticmethod
    def _build_menu_section(menu_items: List[Dict[str, Any]]) -> str:
        """Build the menu items section of the prompt"""
        sections = ["AVAILABLE MENU ITEMS:"]

        for item in menu_items:
            name = item.get("name", "Unknown Item")
            description = item.get("description", "")
            price = item.get("price", 0)
            category = item.get("category", "")

            item_line = f"- {name}"
            if category:
                item_line += f" ({category})"
            if description:
                item_line += f": {description}"
            if price:
                item_line += f" - ${price}"

            sections.append(item_line)

        return "\n".join(sections)

    @staticmethod
    def _build_reviews_section(reviews: List[Dict[str, Any]]) -> str:
        """Build the reviews section of the prompt"""
        sections = ["CUSTOMER REVIEWS:"]

        for review in reviews[:5]:  # Limit to top 5 reviews
            rating = review.get("rating", 0)
            text = review.get("text", "")
            author = review.get("author_name", "Anonymous")

            if text:
                sections.append(f"- {author} ({rating}/5): {text[:150]}...")

        return "\n".join(sections)

    @staticmethod
    def _build_community_section(community_data: List[Dict[str, Any]]) -> str:
        """Build the community favorites section of the prompt"""
        sections = ["COMMUNITY FAVORITES:"]

        for item in community_data:
            name = item.get("item_name", item.get("name", "Unknown"))
            friend_recs = item.get("friend_recommendations", 0)
            community_recs = item.get("community_recommendations", 0)
            avg_rating = item.get("average_rating", 0)

            item_line = f"- {name}"
            if friend_recs > 0:
                item_line += f" ({friend_recs} friend recommendations"
            if community_recs > 0:
                if friend_recs > 0:
                    item_line += f", {community_recs} community votes"
                else:
                    item_line += f" ({community_recs} community votes"
            if avg_rating > 0:
                item_line += f", {avg_rating:.1f}/5 avg rating"
            if friend_recs > 0 or community_recs > 0:
                item_line += ")"

            sections.append(item_line)

        return "\n".join(sections)

    @staticmethod
    def _build_response_format_section() -> str:
        """Build the response format instructions"""
        return """RESPONSE FORMAT:
Please respond with a JSON object containing:
{
    "recommended_item": "exact menu item name from the list above",
    "reasoning": "detailed explanation (2-3 sentences) of why this item matches the user's preferences, incorporating their taste profile, dietary needs, and social proof",
    "confidence": 0.85,
    "backup_recommendation": "alternative item name (optional)"
}

IMPORTANT GUIDELINES:
1. Only recommend items from the menu list provided
2. Avoid any items the user has already rejected
3. Consider dietary restrictions as hard constraints
4. Weight community favorites and positive reviews heavily
5. Explain your reasoning clearly, mentioning specific preference matches
6. Confidence should be 0.6-0.95 based on how well the item matches"""


class PromptTemplates:
    """Pre-built prompt templates for common scenarios"""

    FIRST_RECOMMENDATION = """This is the user's first recommendation at this restaurant. Focus on:
- Popular items with broad appeal
- Items that match their stated preferences
- Highly-rated community favorites
- Safe choices that align with their dietary restrictions"""

    FOLLOW_UP_RECOMMENDATION = """The user has rejected {rejected_count} items. Focus on:
- Items with different flavor profiles from rejected ones
- More adventurous or unique options
- Items that address potential concerns from rejections
- Consider if they're being picky about specific attributes"""

    DIETARY_FOCUSED = """This user has specific dietary restrictions: {restrictions}. Focus on:
- Items that are completely safe for their restrictions
- Highlight how the recommended item meets their needs
- Avoid any items with potential allergens or restricted ingredients
- Emphasize the safety and suitability of your recommendation"""
