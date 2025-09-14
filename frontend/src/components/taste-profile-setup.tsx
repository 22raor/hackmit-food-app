"use client"

import { useState } from "react"
import { components } from "@/types/api-types"

type DietaryRestriction = components["schemas"]["DietaryRestriction"]
type CuisinePreference = components["schemas"]["CuisinePreference"]
type FlavorProfile = components["schemas"]["FlavorProfile"]
type FoodItem = components["schemas"]["FoodItem"]
type UpdateTasteProfile = components["schemas"]["UpdateTasteProfile"]

interface TasteProfileSetupProps {
  userId: string
  onComplete: () => void
}

const COMMON_CUISINES = [
  "Italian", "Chinese", "Japanese", "Mexican", "Indian", "Thai", "French",
  "American", "Mediterranean", "Greek", "Korean", "Vietnamese"
]

const DIETARY_RESTRICTIONS = [
  { name: "Vegetarian", severity: "moderate" },
  { name: "Vegan", severity: "strict" },
  { name: "Gluten-free", severity: "moderate" },
  { name: "Dairy-free", severity: "moderate" },
  { name: "Nut allergy", severity: "severe" },
  { name: "Shellfish allergy", severity: "severe" },
  { name: "Kosher", severity: "moderate" },
  { name: "Halal", severity: "moderate" }
]

const PRICE_RANGES = ["low", "medium", "high"]

export function TasteProfileSetup({ userId, onComplete }: TasteProfileSetupProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState(1)

  const [dietaryRestrictions, setDietaryRestrictions] = useState<DietaryRestriction[]>([])
  const [cuisinePreferences, setCuisinePreferences] = useState<CuisinePreference[]>([])
  const [flavorProfile, setFlavorProfile] = useState<FlavorProfile>({
    spicy_tolerance: 3,
    sweet_preference: 3,
    salty_preference: 3,
    sour_preference: 3,
    umami_preference: 3,
    bitter_tolerance: 3
  })
  const [likedFoods, setLikedFoods] = useState<string>("")
  const [dislikedFoods, setDislikedFoods] = useState<string>("")
  const [priceRangePreference, setPriceRangePreference] = useState<string>("medium")

  const toggleDietaryRestriction = (restriction: DietaryRestriction) => {
    setDietaryRestrictions(prev =>
      prev.find(r => r.name === restriction.name)
        ? prev.filter(r => r.name !== restriction.name)
        : [...prev, restriction]
    )
  }

  const updateCuisinePreference = (cuisineType: string, level: number) => {
    setCuisinePreferences(prev => {
      const existing = prev.find(c => c.cuisine_type === cuisineType)
      if (existing) {
        return prev.map(c =>
          c.cuisine_type === cuisineType
            ? { ...c, preference_level: level }
            : c
        )
      } else {
        return [...prev, { cuisine_type: cuisineType, preference_level: level }]
      }
    })
  }

  const handleSubmit = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const likedFoodItems: FoodItem[] = likedFoods
        .split(",")
        .map(food => food.trim())
        .filter(food => food.length > 0)
        .map(food => ({ name: food, tags: [] }))

      const dislikedFoodItems: FoodItem[] = dislikedFoods
        .split(",")
        .map(food => food.trim())
        .filter(food => food.length > 0)
        .map(food => ({ name: food, tags: [] }))

      const profile: UpdateTasteProfile = {
        dietary_restrictions: dietaryRestrictions,
        cuisine_preferences: cuisinePreferences.filter(c => c.preference_level > 0),
        flavor_profile: flavorProfile,
        liked_foods: likedFoodItems,
        disliked_foods: dislikedFoodItems,
        favorite_restaurants: [],
        price_range_preference: priceRangePreference,
        meal_time_preferences: {}
      }

      const response = await fetch(`/api/user-profile/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to save profile")
      }

      onComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile")
    } finally {
      setIsLoading(false)
    }
  }

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-4">Dietary Restrictions</h3>
        <div className="grid grid-cols-2 gap-3">
          {DIETARY_RESTRICTIONS.map((restriction) => (
            <button
              key={restriction.name}
              onClick={() => toggleDietaryRestriction(restriction)}
              className={`p-3 rounded-lg border text-left transition-colors ${
                dietaryRestrictions.find(r => r.name === restriction.name)
                  ? "bg-blue-50 border-blue-300 text-blue-900"
                  : "bg-white border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="font-medium">{restriction.name}</div>
              <div className="text-sm text-gray-500">{restriction.severity}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-4">Cuisine Preferences</h3>
        <p className="text-sm text-gray-600 mb-4">Rate your preference for each cuisine (1-5 scale, 0 to skip)</p>
        <div className="space-y-3">
          {COMMON_CUISINES.map((cuisine) => (
            <div key={cuisine} className="flex items-center justify-between p-3 bg-white border rounded-lg">
              <span className="font-medium">{cuisine}</span>
              <div className="flex space-x-2">
                {[0, 1, 2, 3, 4, 5].map((level) => (
                  <button
                    key={level}
                    onClick={() => updateCuisinePreference(cuisine, level)}
                    className={`w-8 h-8 rounded-full border text-sm font-medium transition-colors ${
                      cuisinePreferences.find(c => c.cuisine_type === cuisine)?.preference_level === level
                        ? level === 0 ? "bg-gray-200 border-gray-400" : "bg-blue-500 border-blue-500 text-white"
                        : "bg-white border-gray-300 hover:border-gray-400"
                    }`}
                  >
                    {level === 0 ? "×" : level}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-4">Flavor Profile</h3>
        <p className="text-sm text-gray-600 mb-4">Rate your preferences (1-5 scale)</p>
        <div className="space-y-4">
          {[
            { key: "spicy_tolerance" as keyof FlavorProfile, label: "Spicy Tolerance" },
            { key: "sweet_preference" as keyof FlavorProfile, label: "Sweet Preference" },
            { key: "salty_preference" as keyof FlavorProfile, label: "Salty Preference" },
            { key: "sour_preference" as keyof FlavorProfile, label: "Sour Preference" },
            { key: "umami_preference" as keyof FlavorProfile, label: "Umami Preference" },
            { key: "bitter_tolerance" as keyof FlavorProfile, label: "Bitter Tolerance" }
          ].map(({ key, label }) => (
            <div key={key} className="flex items-center justify-between p-3 bg-white border rounded-lg">
              <span className="font-medium">{label}</span>
              <input
                type="range"
                min="1"
                max="5"
                value={flavorProfile[key]}
                onChange={(e) => setFlavorProfile(prev => ({
                  ...prev,
                  [key]: parseInt(e.target.value)
                }))}
                className="w-32"
              />
              <span className="w-8 text-center font-medium">{flavorProfile[key]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const renderStep4 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-4">Food Preferences</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Liked Foods</label>
            <textarea
              value={likedFoods}
              onChange={(e) => setLikedFoods(e.target.value)}
              placeholder="Enter foods you like, separated by commas (e.g., pasta, pizza, sushi)"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Disliked Foods</label>
            <textarea
              value={dislikedFoods}
              onChange={(e) => setDislikedFoods(e.target.value)}
              placeholder="Enter foods you dislike, separated by commas (e.g., mushrooms, olives)"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Price Range Preference</label>
            <div className="flex space-x-3">
              {PRICE_RANGES.map((range) => (
                <button
                  key={range}
                  onClick={() => setPriceRangePreference(range)}
                  className={`px-4 py-2 rounded-lg border font-medium capitalize transition-colors ${
                    priceRangePreference === range
                      ? "bg-blue-500 border-blue-500 text-white"
                      : "bg-white border-gray-300 hover:border-gray-400"
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold text-gray-900">Set Up Your Taste Profile</h1>
              <span className="text-sm text-gray-500">Step {step} of 4</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(step / 4) * 100}%` }}
              />
            </div>
          </div>

          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="mt-8 flex justify-between">
            {step > 1 && (
              <button
                onClick={() => setStep(step - 1)}
                className="px-6 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Previous
              </button>
            )}
            <div className="flex-1" />
            {step < 4 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="px-8 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? "Saving..." : "Complete Setup"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}