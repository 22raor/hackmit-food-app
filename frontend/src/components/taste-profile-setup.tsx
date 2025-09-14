"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { updateUserProfile } from "@/lib/api"
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
  const { data: session } = useSession()
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

      if (!session?.access_token) {
        throw new Error("No authentication token available")
      }

      await updateUserProfile(session.access_token, userId, profile)

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
                    className={`w-10 h-10 rounded-full border text-sm font-medium transition-colors ${
                      cuisinePreferences.find(c => c.cuisine_type === cuisine)?.preference_level === level
                        ? level === 0 ? "bg-gray-200 border-gray-400 text-gray-600" : "bg-[#212528] border-[#212528] text-white"
                        : "bg-white border-[#e6e6e6] hover:border-[#212528] text-[#555555]"
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

  const StatusBar = () => (
    <div className="flex justify-between items-center h-[54px] px-4 bg-[#f5f6f8]">
      <div className="w-[138px] flex justify-center">
        <span className="font-semibold text-[17px] text-black">9:41</span>
      </div>
      <div className="w-[143px]"></div>
    </div>
  )

  const ProgressBar = () => {
    const totalSteps = 9 // Updated to include all steps
    const progressWidth = (step / totalSteps) * 281 // 281px is the width from Figma

    return (
      <div className="px-14 mb-6">
        <div className="relative">
          <div className="w-[281px] h-2 bg-white rounded-[4px]"></div>
          <div
            className="absolute top-0 left-0 h-2 bg-[#212528] rounded-[4px] transition-all duration-300"
            style={{ width: `${progressWidth}px` }}
          ></div>
        </div>
      </div>
    )
  }

  const SliderWithEmojis = ({
    title,
    description,
    emojis,
    labels,
    value,
    onChange
  }: {
    title: string
    description: string
    emojis: string[]
    labels: string[]
    value: number
    onChange: (value: number) => void
  }) => (
    <div className="px-12">
      <h1 className="text-[38px] font-bold text-black leading-[45px] mb-4">
        {title}
      </h1>

      <p className="text-[#555555] text-[12px] leading-4 mb-16">
        {description}
      </p>

      <div className="mb-8">
        <div className="flex justify-between items-center mb-4 px-4">
          {emojis.map((emoji, index) => (
            <span key={index} className="text-[24px]">{emoji}</span>
          ))}
        </div>

        <div className="relative mb-4 px-2">
          <input
            type="range"
            min="1"
            max="5"
            step="1"
            value={value}
            onChange={(e) => onChange(parseInt(e.target.value))}
            className="w-full h-2.5 bg-white border border-[#e6e6e6] rounded-[14px] appearance-none cursor-pointer slider-custom"
            style={{
              background: `linear-gradient(to right, #212528 0%, #212528 ${((value - 1) / 4) * 100}%, #ffffff ${((value - 1) / 4) * 100}%, #ffffff 100%)`
            }}
          />
        </div>

        <div className="flex justify-between text-[14px] font-semibold text-black text-center px-4">
          {labels.map((label, index) => (
            <span key={index} className="w-[73px]">{label}</span>
          ))}
        </div>
      </div>

      <div className="text-right pr-8 mb-8">
        <button
          onClick={() => setStep(step + 1)}
          className="text-[#555555] text-[12px] underline hover:no-underline"
        >
          Skip
        </button>
      </div>
    </div>
  )

  const renderFlavorStep = (
    stepNum: number,
    flavorKey: keyof FlavorProfile,
    title: string,
    description: string,
    emojis: string[],
    labels: string[]
  ) => {
    if (step !== stepNum) return null

    return (
      <SliderWithEmojis
        title={title}
        description={description}
        emojis={emojis}
        labels={labels}
        value={flavorProfile[flavorKey]}
        onChange={(value) => setFlavorProfile(prev => ({
          ...prev,
          [flavorKey]: value
        }))}
      />
    )
  }

  const renderDietaryStep = () => {
    if (step !== 5) return null

    return (
      <div className="px-12">
        <h1 className="text-[38px] font-bold text-black leading-[45px] mb-4">
          Any diet-based restrictions?
        </h1>

        <div className="grid grid-cols-2 gap-4 mb-8">
          {DIETARY_RESTRICTIONS.slice(0, 6).map((restriction) => (
            <button
              key={restriction.name}
              onClick={() => toggleDietaryRestriction(restriction)}
              className={`h-[51px] rounded-[13px] flex items-center justify-center text-[14px] font-normal transition-colors ${
                dietaryRestrictions.find(r => r.name === restriction.name)
                  ? "bg-[#212528] text-white"
                  : "bg-white border border-[#e6e6e6] text-black hover:border-[#212528]"
              }`}
            >
              {restriction.name}
            </button>
          ))}
        </div>

        <div className="text-right pr-8 mb-8">
          <button
            onClick={() => setStep(step + 1)}
            className="text-[#555555] text-[12px] underline hover:no-underline"
          >
            Skip
          </button>
        </div>
      </div>
    )
  }

  const renderAllergiesStep = () => {
    if (step !== 6) return null

    return (
      <div className="px-12">
        <h1 className="text-[38px] font-bold text-black leading-[45px] mb-4">
          Allergies?
        </h1>
        <p className="text-[#555555] text-[12px] leading-4 mb-8">
          And intolerances!
        </p>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search"
            className="w-full h-[51px] bg-white border border-[#e6e6e6] rounded-[13px] px-4 text-base placeholder-[#555555] focus:outline-none focus:border-[#212528]"
          />
        </div>

        <div className="flex gap-2 mb-8">
          <span className="bg-[#212528] text-white px-3 py-1 rounded-[17px] text-[12px] flex items-center gap-2">
            Peanuts
            <button className="text-white hover:text-gray-300">×</button>
          </span>
          <span className="bg-[#212528] text-white px-3 py-1 rounded-[17px] text-[12px] flex items-center gap-2">
            Dairy
            <button className="text-white hover:text-gray-300">×</button>
          </span>
        </div>

        <div className="text-right pr-8 mb-8">
          <button
            onClick={() => setStep(step + 1)}
            className="text-[#555555] text-[12px] underline hover:no-underline"
          >
            Skip
          </button>
        </div>
      </div>
    )
  }

  const renderBudgetStep = () => {
    if (step !== 7) return null

    return (
      <div className="px-12">
        <h1 className="text-[38px] font-bold text-black leading-[45px] mb-4">
          Reality check
        </h1>
        <p className="text-[#555555] text-[12px] leading-4 mb-16">
          How much are you willing to spend for food?
        </p>

        <div className="space-y-4 mb-8">
          {PRICE_RANGES.map((range) => (
            <button
              key={range}
              onClick={() => setPriceRangePreference(range)}
              className={`w-full h-[51px] rounded-[13px] flex items-center justify-center text-[14px] font-normal transition-colors ${
                priceRangePreference === range
                  ? "bg-[#212528] text-white"
                  : "bg-white border border-[#e6e6e6] text-black hover:border-[#212528]"
              }`}
            >
              {range === 'low' ? '$0-15' : range === 'medium' ? '$15-30' : '$30+'}
            </button>
          ))}
        </div>

        <div className="text-right pr-8 mb-8">
          <button
            onClick={() => setStep(step + 1)}
            className="text-[#555555] text-[12px] underline hover:no-underline"
          >
            Skip
          </button>
        </div>
      </div>
    )
  }

  const renderFoodPreferencesStep = () => {
    if (step !== 8) return null

    return (
      <div className="px-12">
        <h1 className="text-[38px] font-bold text-black leading-[45px] mb-4">
          Food Preferences
        </h1>
        <p className="text-[#555555] text-[12px] leading-4 mb-8">
          Tell us what you love and what to avoid
        </p>

        <div className="space-y-6 mb-8">
          <div>
            <label className="block text-[16px] font-semibold text-black mb-2">
              Liked Foods
            </label>
            <textarea
              value={likedFoods}
              onChange={(e) => setLikedFoods(e.target.value)}
              placeholder="e.g., pasta, sushi, chocolate"
              className="w-full h-[80px] bg-white border border-[#e6e6e6] rounded-[13px] px-4 py-3 text-[14px] placeholder-[#555555] focus:outline-none focus:border-[#212528] resize-none"
            />
          </div>

          <div>
            <label className="block text-[16px] font-semibold text-black mb-2">
              Disliked Foods
            </label>
            <textarea
              value={dislikedFoods}
              onChange={(e) => setDislikedFoods(e.target.value)}
              placeholder="e.g., mushrooms, olives, seafood"
              className="w-full h-[80px] bg-white border border-[#e6e6e6] rounded-[13px] px-4 py-3 text-[14px] placeholder-[#555555] focus:outline-none focus:border-[#212528] resize-none"
            />
          </div>
        </div>

        <div className="text-right pr-8 mb-8">
          <button
            onClick={() => setStep(step + 1)}
            className="text-[#555555] text-[12px] underline hover:no-underline"
          >
            Skip
          </button>
        </div>
      </div>
    )
  }

  const renderCuisineStep = () => {
    if (step !== 9) return null

    return (
      <div className="px-12">
        <h1 className="text-[38px] font-bold text-black leading-[45px] mb-8">
          Cuisine Preferences
        </h1>

        <div className="space-y-3 mb-8">
          {COMMON_CUISINES.slice(0, 8).map((cuisine) => {
            const preference = cuisinePreferences.find(c => c.cuisine_type === cuisine)
            const level = preference?.preference_level || 0

            return (
              <div key={cuisine} className="bg-white border border-[#e6e6e6] rounded-[13px] p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-black text-[14px]">{cuisine}</span>
                  <span className="text-[12px] text-[#555555]">
                    {level === 0 ? 'Skip' : `${level}/5`}
                  </span>
                </div>
                <div className="flex justify-between items-center gap-1">
                  {[0, 1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => updateCuisinePreference(cuisine, rating)}
                      className={`flex-1 h-8 max-w-[48px] rounded-full border text-xs font-medium transition-colors ${
                        level === rating
                          ? rating === 0
                            ? "bg-gray-200 border-gray-400 text-gray-600"
                            : "bg-[#212528] border-[#212528] text-white"
                          : "bg-white border-[#e6e6e6] hover:border-[#212528] text-[#555555]"
                      }`}
                    >
                      {rating === 0 ? "×" : rating}
                    </button>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        <div className="text-right pr-8 mb-8">
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="text-[#555555] text-[12px] underline hover:no-underline disabled:opacity-50"
          >
            {isLoading ? "Saving..." : "Skip"}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mobile-container">
      <StatusBar />
      <ProgressBar />

      <div className="flex-1">
        {renderFlavorStep(
          1,
          "spicy_tolerance",
          "What's your heat tolerance?",
          "From 'call the fire department' to 'is this even seasoned'?",
          ["😴", "🫑", "🌋"],
          ["Bland", "Moderate", "Lava!"]
        )}

        {renderFlavorStep(
          2,
          "sweet_preference",
          "Are you a sweet tooth?",
          "Are you a dessert-for-breakfast person or do you avoid sugar like a vampire avoids garlic?",
          ["🚫", "🍯", "🍭"],
          ["No sugar", "Moderate", "Candy shop"]
        )}

        {renderFlavorStep(
          3,
          "salty_preference",
          "How about the saltiness?",
          "How much 'flavor' do you prefer?",
          ["🥬", "⚖️", "🌊"],
          ["Low salt", "Moderate", "Ocean water"]
        )}

        {renderFlavorStep(
          4,
          "sour_preference",
          "What about sourness?",
          "&quot;I down a lemon a day!&quot;",
          ["😐", "😋", "🍋"],
          ["Nope", "Moderate", "Real sour"]
        )}

        {renderDietaryStep()}
        {renderAllergiesStep()}
        {renderBudgetStep()}
        {renderFoodPreferencesStep()}
        {renderCuisineStep()}

        {error && (
          <div className="mx-4 mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {step < 9 && step > 0 && (
          <div className="px-12 mt-8">
            <button
              onClick={() => setStep(step + 1)}
              disabled={isLoading}
              className="w-full h-[42px] bg-[#212528] text-white rounded-[13px] font-normal text-base hover:bg-[#313538] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {step === 8 ? "Continue" : "Next"}
            </button>
          </div>
        )}

        {step === 9 && (
          <div className="px-12 mt-8">
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full h-[42px] bg-[#212528] text-white rounded-[13px] font-normal text-base hover:bg-[#313538] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? "Saving..." : "Complete Setup"}
            </button>
          </div>
        )}
      </div>

      {/* Home indicator */}
      <div className="w-[115px] h-[5px] bg-[#212528] rounded-[25px] mx-auto mt-auto mb-4"></div>
    </div>
  )
}