"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { components } from "@/types/api-types"
import { MobileLayout } from "@/components/ui/mobile-layout"
import { useUser } from "@/hooks/useUser"
import { AuthFailurePage } from "@/components/auth-failure-page"
import Link from "next/link"
import { signOut } from "next-auth/react"

type FoodItemRecommendation = components["schemas"]["FoodItemRecommendation"]

export default function RecommendationPage() {
  const { isAuthenticated, loading } = useUser()
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <AuthFailurePage />
  }

  if (!item) {
    return (
      <MobileLayout>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p>Loading your recommendation...</p>
          </div>
        </div>
      </MobileLayout>
    )
  }

  return (
    <MobileLayout>
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 flex items-center justify-between border-b border-[#e6e6e6] bg-white">
          <Link href="/restaurants" className="text-[#555555] hover:text-black">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6">
              <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </Link>
          <h1 className="text-[20px] font-semibold text-black">Recommendation</h1>
          <button
            onClick={() => signOut()}
            className="text-[#555555] text-[14px] hover:text-[#212528] transition-colors"
          >
            Logout
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {/* Food Image */}
          <div className="h-[250px] bg-gray-200 relative">
            {item.image_url ? (
              <img
                src={item.image_url}
                alt={item.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-r from-gray-100 to-gray-200 flex items-center justify-center">
                <svg viewBox="0 0 24 24" fill="none" className="w-16 h-16 text-gray-400">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M8.5 10.5h3M8.5 13.5h7M8.5 16.5h7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
            )}
          </div>

          <div className="p-6">
            {/* Title and Price */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h1 className="text-[22px] font-semibold text-black mb-2">
                  {item.name}
                </h1>
                <span className="bg-[#f5f6f8] text-[#555555] px-3 py-1 rounded-[17px] text-[12px]">
                  {item.category}
                </span>
              </div>
              <div className="text-right">
                <div className="text-[24px] font-bold text-black mb-1">
                  ${item.price}
                </div>
                {item.calories && (
                  <div className="text-[#555555] text-[12px]">
                    {item.calories} cal
                  </div>
                )}
              </div>
            </div>

            {/* Description */}
            <div className="mb-6">
              <p className="text-[#555555] text-[14px] leading-6">
                {item.description}
              </p>
            </div>

            {/* Dietary Tags */}
            <div className="flex gap-2 mb-6">
              <span className="bg-[#f5f6f8] text-[#555555] px-3 py-1 rounded-[17px] text-[11px]">
                Vegetarian
              </span>
              <span className="bg-[#f5f6f8] text-[#555555] px-3 py-1 rounded-[17px] text-[11px]">
                Gluten-free
              </span>
            </div>

            {/* Ingredients */}
            {item.ingredients.length > 0 && (
              <div className="mb-6">
                <h2 className="text-[18px] font-semibold text-black mb-3">Ingredients</h2>
                <div className="flex flex-wrap gap-2">
                  {item.ingredients.map((ingredient, index) => (
                    <span
                      key={index}
                      className="bg-white border border-[#e6e6e6] text-[#555555] px-3 py-2 rounded-[13px] text-[12px]"
                    >
                      {ingredient}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Allergens */}
            {item.allergens.length > 0 && (
              <div className="mb-6">
                <h2 className="text-[18px] font-semibold text-black mb-3">Allergens</h2>
                <div className="flex flex-wrap gap-2">
                  {item.allergens.map((allergen, index) => (
                    <span
                      key={index}
                      className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-[13px] text-[12px] font-medium"
                    >
                      ⚠️ {allergen}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Why recommended */}
            {item.reasoning && (
              <div className="bg-[#f5f6f8] rounded-[13px] p-4 mb-6">
                <h2 className="text-[16px] font-semibold text-black mb-2">
                  Why this recommendation?
                </h2>
                <p className="text-[#555555] text-[14px] leading-5">
                  {item.reasoning}
                </p>
              </div>
            )}

            {/* Reviews */}
            {item.reviews.length > 0 && (
              <div className="mb-6">
                <h2 className="text-[18px] font-semibold text-black mb-4">
                  Reviews
                </h2>
                <div className="space-y-4">
                  {item.reviews.slice(0, 3).map((review, index) => (
                    <div key={index} className="bg-white border border-[#e6e6e6] rounded-[13px] p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <div className="flex text-yellow-400 mr-2">
                            {[...Array(5)].map((_, i) => (
                              <span key={i} className="text-[12px]">
                                {i < (review.rating || 0) ? "★" : "☆"}
                              </span>
                            ))}
                          </div>
                          {review.author && (
                            <span className="text-[12px] text-[#555555] font-medium">
                              {review.author}
                            </span>
                          )}
                        </div>
                        {review.date && (
                          <span className="text-[10px] text-[#555555]">{review.date}</span>
                        )}
                      </div>
                      <p className="text-[#555555] text-[13px] leading-5">{review.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Button */}
            <div className="pt-4">
              <Link href="/" className="block w-full">
                <button className="w-full h-[48px] bg-[#212528] text-white rounded-[13px] font-medium text-base hover:bg-[#313538] transition-colors">
                  Add to Order
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </MobileLayout>
  )
}