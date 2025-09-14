"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { components } from "@/types/api-types"
import { RestaurantCard } from "./restaurant-card"
import { RecommendationDisplay } from "./recommendation-display"
import { MobileLayout } from "./ui/mobile-layout"
import Link from "next/link"
import { signOut } from "next-auth/react"

type User = components["schemas"]["UserResponse"]
type NearbyRestaurantsResponse = components["schemas"]["NearbyRestaurantsResponse"]
type Restaurant = components["schemas"]["Restaurant"]
type FoodItemRecommendation = components["schemas"]["FoodItemRecommendation"]

interface RestaurantsViewProps {
  user?: User | null
}

export function RestaurantsView({ user }: RestaurantsViewProps) {
  const router = useRouter()
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null)

  useEffect(() => {
    fetchNearbyRestaurants()
  }, [])

  const fetchNearbyRestaurants = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch('/api/restaurants', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch restaurants: ${response.status}`)
      }

      const data: NearbyRestaurantsResponse = await response.json()
      setRestaurants(data.restaurants)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch restaurants')
    } finally {
      setLoading(false)
    }
  }

  const handleRestaurantClick = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant)
  }

  const handleRecommendationClose = () => {
    setSelectedRestaurant(null)
  }

  const handleRecommendationApprove = (item: FoodItemRecommendation) => {
    // Store the item in localStorage and navigate to the recommendation page
    localStorage.setItem(`recommendation_${item.id}`, JSON.stringify(item))
    router.push(`/recommendation/${item.id}`)
  }

  if (loading) {
    return (
      <MobileLayout>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p>Finding nearby restaurants...</p>
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
          <Link href="/" className="text-[#555555] hover:text-black">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6">
              <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </Link>
          <h1 className="text-[20px] font-semibold text-black">Restaurants</h1>
          <button
            onClick={() => signOut()}
            className="text-[#555555] text-[14px] hover:text-[#212528] transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Category Tabs */}
        <div className="px-4 mb-6">
          <div className="flex gap-2">
            <button className="bg-[#212528] text-white px-4 py-2 rounded-[25px] text-[14px] font-medium">
              All
            </button>
            <button className="bg-white border border-[#e6e6e6] text-black px-4 py-2 rounded-[25px] text-[14px] font-medium hover:border-[#212528] transition-colors">
              Appetizers
            </button>
            <button className="bg-white border border-[#e6e6e6] text-black px-4 py-2 rounded-[25px] text-[14px] font-medium hover:border-[#212528] transition-colors">
              Main Course
            </button>
            <button className="bg-white border border-[#e6e6e6] text-black px-4 py-2 rounded-[25px] text-[14px] font-medium hover:border-[#212528] transition-colors">
              Dessert
            </button>
          </div>
        </div>

        {error && (
          <div className="mx-6 mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-[13px]">
            {error}
            <button
              onClick={fetchNearbyRestaurants}
              className="ml-4 text-red-800 underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Restaurant Grid */}
        <div className="flex-1 px-6">
          {restaurants.length === 0 && !error ? (
            <div className="text-center py-12">
              <p className="text-[#555555] text-lg">No restaurants found nearby</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 desktop-restaurant-grid gap-6 pb-6">
              {restaurants.map((restaurant) => (
                <div
                  key={restaurant.id}
                  onClick={() => handleRestaurantClick(restaurant)}
                  className="bg-white rounded-[13px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)] overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
                >
                  <div className="h-[150px] bg-gray-200 relative">
                    {restaurant.image_url ? (
                      <img
                        src={restaurant.image_url}
                        alt={restaurant.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-r from-gray-100 to-gray-200 flex items-center justify-center">
                        <svg viewBox="0 0 24 24" fill="none" className="w-12 h-12 text-gray-400">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" stroke="currentColor" strokeWidth="2"/>
                          <path d="M8.5 10.5h3M8.5 13.5h7M8.5 16.5h7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                      </div>
                    )}
                  </div>

                  <div className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-[16px] text-black">{restaurant.name}</h3>
                      <div className="flex items-center">
                        <svg viewBox="0 0 24 24" fill="#FFD700" className="w-4 h-4 mr-1">
                          <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z"/>
                        </svg>
                        <span className="text-[#313131] text-[12px] font-medium">
                          {restaurant.rating || '4.5'}
                        </span>
                      </div>
                    </div>

                    <p className="text-[#555555] text-[12px] mb-2">
                      {restaurant.category || 'American'} • $15-25
                    </p>

                    <p className="text-[#555555] text-[11px] mb-3">
                      {restaurant.address || 'Address not available'}
                    </p>

                    <div className="flex gap-2">
                      <span className="bg-[#f5f6f8] text-[#555555] px-2 py-1 rounded-[17px] text-[10px]">
                        Vegetarian
                      </span>
                      <span className="bg-[#f5f6f8] text-[#555555] px-2 py-1 rounded-[17px] text-[10px]">
                        Gluten-free
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedRestaurant && (
          <RecommendationDisplay
            restaurantId={selectedRestaurant.id}
            restaurantName={selectedRestaurant.name}
            onClose={handleRecommendationClose}
            onApprove={handleRecommendationApprove}
          />
        )}
      </div>
    </MobileLayout>
  )
}