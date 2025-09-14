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
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Recommendation for {restaurantName}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Getting your recommendation...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
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
              <div className="bg-gray-50 rounded-lg p-6">
                {recommendation.item.image_url && (
                  <img
                    src={recommendation.item.image_url}
                    alt={recommendation.item.name}
                    className="w-full h-48 object-cover rounded-lg mb-4"
                  />
                )}

                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {recommendation.item.name}
                  </h3>
                  <span className="text-lg font-bold text-green-600">
                    ${recommendation.item.price}
                  </span>
                </div>

                <p className="text-gray-700 mb-4">
                  {recommendation.item.description}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Category</h4>
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                      {recommendation.item.category}
                    </span>
                  </div>

                  {recommendation.item.calories && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Calories</h4>
                      <span className="text-gray-700">{recommendation.item.calories}</span>
                    </div>
                  )}
                </div>

                {recommendation.item.ingredients.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">Ingredients</h4>
                    <div className="flex flex-wrap gap-2">
                      {recommendation.item.ingredients.map((ingredient, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-200 text-gray-700 text-sm rounded"
                        >
                          {ingredient}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {recommendation.item.allergens.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">Allergens</h4>
                    <div className="flex flex-wrap gap-2">
                      {recommendation.item.allergens.map((allergen, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-red-100 text-red-800 text-sm rounded"
                        >
                          {allergen}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 rounded-lg p-4 mb-6">
                  <h4 className="font-medium text-blue-900 mb-2">Why we recommend this</h4>
                  <p className="text-blue-800 text-sm">{recommendation.item.reasoning}</p>
                  <div className="mt-2">
                    <span className="text-xs text-blue-600">
                      Confidence: {Math.round(recommendation.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleDeny}
                  className="flex-1 px-6 py-3 border-2 border-red-200 text-red-700 rounded-lg hover:bg-red-50 transition-colors font-medium"
                >
                  Not interested
                </button>
                <button
                  onClick={handleApprove}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                >
                  I'll take it!
                </button>
              </div>

              {currentDislikes.length > 0 && (
                <div className="mt-4 text-sm text-gray-500">
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