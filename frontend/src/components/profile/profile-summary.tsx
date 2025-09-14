import { components } from "@/types/api-types"

interface ProfileSummaryProps {
  profile: {
    dietary_restrictions: components["schemas"]["DietaryRestriction"][]
    cuisine_preferences: components["schemas"]["CuisinePreference"][]
    liked_foods: components["schemas"]["FoodItem"][]
  }
}

export function ProfileSummary({ profile }: ProfileSummaryProps) {
  const hasPreferences =
    profile.dietary_restrictions.length > 0 ||
    profile.cuisine_preferences.length > 0 ||
    profile.liked_foods.length > 0

  if (!hasPreferences) {
    return (
      <p className="text-sm text-gray-500 italic">
        No dietary restrictions, cuisine preferences, or liked foods set
      </p>
    )
  }

  return (
    <div className="space-y-3 text-left">
      <p className="text-gray-600">Profile configured with:</p>
      <ul className="text-sm space-y-1">
        {profile.dietary_restrictions.length > 0 && (
          <li>• {profile.dietary_restrictions.length} dietary restrictions</li>
        )}
        {profile.cuisine_preferences.length > 0 && (
          <li>• {profile.cuisine_preferences.length} cuisine preferences</li>
        )}
        {profile.liked_foods.length > 0 && (
          <li>• {profile.liked_foods.length} liked foods</li>
        )}
      </ul>
    </div>
  )
}