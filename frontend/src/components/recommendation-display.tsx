"use client"

import { useState, useEffect } from "react"
import { components } from "@/types/api-types"

type FoodItemRecommendation = components["schemas"]["FoodItemRecommendation"]
type RecommendationResponse = components["schemas"]["RecommendationResponse"]

interface RecommendationDisplayProps {
  restaurantId: string
  restaurantName: string
  onClose: () => void
  onApprove: (item: FoodItemRecommendation) => void
}

export function RecommendationDisplay({
  restaurantId,
  restaurantName,
  onClose,
  onApprove
}: RecommendationDisplayProps) {
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentDislikes, setCurrentDislikes] = useState<string[]>([])

  const fetchRecommendation = async (dislikes: string[] = []) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/recs/${restaurantId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ curr_dislikes: dislikes }),
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch recommendation: ${response.status}`)
      }

      const data: RecommendationResponse = await response.json()
      setRecommendation(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recommendation')
    } finally {
      setLoading(false)
    }
  }

  const handleDeny = () => {
    if (recommendation) {
      const newDislikes = [...currentDislikes, recommendation.item.name]
      setCurrentDislikes(newDislikes)
      fetchRecommendation(newDislikes)
    }
  }

  const handleApprove = () => {
    if (recommendation) {
      onApprove(recommendation.item)
    }
  }

  // Fetch initial recommendation when component mounts
  useEffect(() => {
    fetchRecommendation()
  }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-[13px] max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)]">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-[20px] font-semibold text-black">
              Recommendation for {restaurantName}
            </h2>
            <button
              onClick={onClose}
              className="text-[#555555] hover:text-black"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#212528]"></div>
              <span className="ml-3 text-[#555555]">Getting your recommendation...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-[13px] mb-4">
              {error}
              <button
                onClick={() => fetchRecommendation(currentDislikes)}
                className="ml-4 text-red-800 underline hover:no-underline"
              >
                Try again
              </button>
            </div>
          )}

          {recommendation && !loading && (
            <div className="space-y-6">
              <div className="bg-[#f5f6f8] rounded-[13px] p-6">
                {recommendation.item.image_url && (
                  <img
                    src={recommendation.item.image_url}
                    alt={recommendation.item.name}
                    className="w-full h-48 object-cover rounded-[13px] mb-4"
                  />
                )}

                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-[18px] font-semibold text-black">
                    {recommendation.item.name}
                  </h3>
                  <span className="text-[16px] font-bold text-black">
                    ${recommendation.item.price}
                  </span>
                </div>

                <p className="text-[#555555] text-[14px] mb-4 leading-6">
                  {recommendation.item.description}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h4 className="font-medium text-black mb-2 text-[14px]">Category</h4>
                    <span className="px-3 py-1 bg-[#f5f6f8] text-[#555555] text-[12px] rounded-[17px]">
                      {recommendation.item.category}
                    </span>
                  </div>

                  {recommendation.item.calories && (
                    <div>
                      <h4 className="font-medium text-black mb-2 text-[14px]">Calories</h4>
                      <span className="text-[#555555] text-[14px]">{recommendation.item.calories}</span>
                    </div>
                  )}
                </div>

                {recommendation.item.ingredients.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-black mb-2 text-[14px]">Ingredients</h4>
                    <div className="flex flex-wrap gap-2">
                      {recommendation.item.ingredients.map((ingredient, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-white border border-[#e6e6e6] text-[#555555] text-[12px] rounded-[13px]"
                        >
                          {ingredient}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {recommendation.item.allergens.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-black mb-2 text-[14px]">Allergens</h4>
                    <div className="flex flex-wrap gap-2">
                      {recommendation.item.allergens.map((allergen, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-red-50 border border-red-200 text-red-700 text-[12px] rounded-[13px]"
                        >
                          {allergen}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-[#f5f6f8] rounded-[13px] p-4 mb-6">
                  <h4 className="font-medium text-black mb-2 text-[14px]">Why we recommend this</h4>
                  <p className="text-[#555555] text-[14px] leading-5">{recommendation.item.reasoning}</p>
                  <div className="mt-2">
                    <span className="text-[12px] text-[#555555]">
                      Confidence: {Math.round(recommendation.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleDeny}
                  className="flex-1 h-[42px] border border-[#e6e6e6] text-[#555555] rounded-[13px] font-medium text-[14px] hover:border-[#212528] transition-colors"
                >
                  Not interested
                </button>
                <button
                  onClick={handleApprove}
                  className="flex-1 h-[42px] bg-[#212528] text-white rounded-[13px] font-medium text-[14px] hover:bg-[#313538] transition-colors"
                >
                  I'll take it!
                </button>
              </div>

              {currentDislikes.length > 0 && (
                <div className="mt-4 text-[12px] text-[#555555]">
                  <span>Previously shown: {currentDislikes.join(", ")}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}