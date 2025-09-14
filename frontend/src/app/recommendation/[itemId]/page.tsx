"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { components } from "@/types/api-types"

type FoodItemRecommendation = components["schemas"]["FoodItemRecommendation"]

export default function RecommendationPage() {
  const params = useParams()
  const itemId = params.itemId as string
  const [item, setItem] = useState<FoodItemRecommendation | null>(null)

  useEffect(() => {
    // Get the item from localStorage (stored when approved)
    const storedItem = localStorage.getItem(`recommendation_${itemId}`)
    if (storedItem) {
      setItem(JSON.parse(storedItem))
    }
  }, [itemId])

  if (!item) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading your recommendation...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {item.image_url && (
            <div className="h-64 md:h-80 overflow-hidden">
              <img
                src={item.image_url}
                alt={item.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          <div className="p-8">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {item.name}
                </h1>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                  {item.category}
                </span>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  ${item.price}
                </div>
                {item.calories && (
                  <div className="text-gray-600">
                    {item.calories} calories
                  </div>
                )}
              </div>
            </div>

            <div className="prose max-w-none mb-8">
              <p className="text-lg text-gray-700 leading-relaxed">
                {item.description}
              </p>
            </div>

            {item.ingredients.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Ingredients</h2>
                <div className="flex flex-wrap gap-2">
                  {item.ingredients.map((ingredient, index) => (
                    <span
                      key={index}
                      className="px-3 py-2 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {ingredient}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {item.allergens.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Allergens</h2>
                <div className="flex flex-wrap gap-2">
                  {item.allergens.map((allergen, index) => (
                    <span
                      key={index}
                      className="px-3 py-2 bg-red-100 text-red-800 rounded-full text-sm font-medium"
                    >
                      ⚠️ {allergen}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {item.reasoning && (
              <div className="bg-blue-50 rounded-lg p-6 mb-8">
                <h2 className="text-xl font-semibold text-blue-900 mb-3">
                  Why this recommendation?
                </h2>
                <p className="text-blue-800 leading-relaxed">
                  {item.reasoning}
                </p>
              </div>
            )}

            {item.reviews.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  What others are saying
                </h2>
                <div className="space-y-4">
                  {item.reviews.map((review, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <div className="flex text-yellow-400">
                          {[...Array(5)].map((_, i) => (
                            <span key={i}>
                              {i < (review.rating || 0) ? "★" : "☆"}
                            </span>
                          ))}
                        </div>
                        {review.author && (
                          <span className="ml-3 text-sm text-gray-600">
                            - {review.author}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700">{review.text}</p>
                      {review.date && (
                        <p className="text-xs text-gray-500 mt-2">{review.date}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-center">
              <button
                onClick={() => window.history.back()}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Back to Restaurants
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}