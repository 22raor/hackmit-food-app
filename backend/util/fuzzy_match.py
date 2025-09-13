from typing import List, Tuple, Optional
import re
from difflib import SequenceMatcher

class FuzzyMatcher:
    """Utility class for fuzzy string matching operations"""
    
    @staticmethod
    def find_best_match(
        query: str, 
        candidates: List[str], 
        threshold: float = 0.6
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best fuzzy match for a query string among candidates
        
        Args:
            query: The string to match
            candidates: List of candidate strings
            threshold: Minimum similarity score (0-1)
            
        Returns:
            Tuple of (best_match, score) or None if no match above threshold
        """
        if not query or not candidates:
            return None
        
        query_clean = FuzzyMatcher._clean_string(query)
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            candidate_clean = FuzzyMatcher._clean_string(candidate)
            score = FuzzyMatcher._calculate_similarity(query_clean, candidate_clean)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
        
        return (best_match, best_score) if best_match else None
    
    @staticmethod
    def find_all_matches(
        query: str, 
        candidates: List[str], 
        threshold: float = 0.6,
        limit: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """
        Find all fuzzy matches above threshold, sorted by score
        
        Args:
            query: The string to match
            candidates: List of candidate strings
            threshold: Minimum similarity score (0-1)
            limit: Maximum number of results to return
            
        Returns:
            List of (match, score) tuples sorted by score descending
        """
        if not query or not candidates:
            return []
        
        query_clean = FuzzyMatcher._clean_string(query)
        matches = []
        
        for candidate in candidates:
            candidate_clean = FuzzyMatcher._clean_string(candidate)
            score = FuzzyMatcher._calculate_similarity(query_clean, candidate_clean)
            
            if score >= threshold:
                matches.append((candidate, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        
        if limit:
            matches = matches[:limit]
        
        return matches
    
    @staticmethod
    def match_menu_items(
        user_input: str,
        menu_items: List[dict],
        name_field: str = 'name',
        description_field: str = 'description',
        threshold: float = 0.5
    ) -> List[Tuple[dict, float]]:
        """
        Match user input against menu items considering both name and description
        
        Args:
            user_input: User's search query
            menu_items: List of menu item dictionaries
            name_field: Field name for item name
            description_field: Field name for item description
            threshold: Minimum similarity score
            
        Returns:
            List of (menu_item, score) tuples sorted by relevance
        """
        if not user_input or not menu_items:
            return []
        
        user_input_clean = FuzzyMatcher._clean_string(user_input)
        matches = []
        
        for item in menu_items:
            name = item.get(name_field, '')
            description = item.get(description_field, '')
            
            # Calculate scores for name and description
            name_score = FuzzyMatcher._calculate_similarity(
                user_input_clean, 
                FuzzyMatcher._clean_string(name)
            )
            
            desc_score = FuzzyMatcher._calculate_similarity(
                user_input_clean, 
                FuzzyMatcher._clean_string(description)
            )
            
            # Weight name matches higher than description matches
            combined_score = max(name_score * 1.0, desc_score * 0.7)
            
            # Also check for partial word matches
            partial_score = FuzzyMatcher._check_partial_matches(user_input_clean, name, description)
            combined_score = max(combined_score, partial_score)
            
            if combined_score >= threshold:
                matches.append((item, combined_score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    @staticmethod
    def _clean_string(text: str) -> str:
        """Clean and normalize string for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """Calculate similarity score between two strings"""
        if not str1 or not str2:
            return 0.0
        
        # Use SequenceMatcher for basic similarity
        basic_score = SequenceMatcher(None, str1, str2).ratio()
        
        # Bonus for exact word matches
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if words1 and words2:
            word_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
            # Combine scores with word overlap getting some weight
            return max(basic_score, word_overlap * 0.8)
        
        return basic_score
    
    @staticmethod
    def _check_partial_matches(query: str, name: str, description: str) -> float:
        """Check for partial word matches in name and description"""
        query_words = query.split()
        name_clean = FuzzyMatcher._clean_string(name)
        desc_clean = FuzzyMatcher._clean_string(description)
        
        name_matches = 0
        desc_matches = 0
        
        for word in query_words:
            if len(word) >= 3:  # Only consider words of 3+ characters
                if word in name_clean:
                    name_matches += 1
                if word in desc_clean:
                    desc_matches += 1
        
        if not query_words:
            return 0.0
        
        name_partial_score = name_matches / len(query_words)
        desc_partial_score = desc_matches / len(query_words)
        
        # Weight name matches higher
        return max(name_partial_score * 0.8, desc_partial_score * 0.5)

class RestaurantMatcher:
    """Specialized matcher for restaurant-related searches"""
    
    @staticmethod
    def match_cuisine_types(
        user_preference: str,
        available_cuisines: List[str],
        threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """Match user cuisine preference to available cuisine types"""
        return FuzzyMatcher.find_all_matches(
            user_preference,
            available_cuisines,
            threshold
        )
    
    @staticmethod
    def match_dietary_restrictions(
        user_restriction: str,
        menu_items: List[dict],
        allergen_field: str = 'allergens',
        ingredient_field: str = 'ingredients'
    ) -> List[dict]:
        """Find menu items that match dietary restrictions"""
        restriction_clean = FuzzyMatcher._clean_string(user_restriction)
        safe_items = []
        
        for item in menu_items:
            allergens = item.get(allergen_field, [])
            ingredients = item.get(ingredient_field, [])
            
            # Check if restriction matches any allergens or ingredients
            is_safe = True
            
            for allergen in allergens:
                if FuzzyMatcher._calculate_similarity(
                    restriction_clean, 
                    FuzzyMatcher._clean_string(allergen)
                ) > 0.8:
                    is_safe = False
                    break
            
            if is_safe:
                for ingredient in ingredients:
                    if FuzzyMatcher._calculate_similarity(
                        restriction_clean,
                        FuzzyMatcher._clean_string(ingredient)
                    ) > 0.8:
                        is_safe = False
                        break
            
            if is_safe:
                safe_items.append(item)
        
        return safe_items
