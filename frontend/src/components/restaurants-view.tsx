"use client"

import { useState, useEffect } from "react"
import { components } from "@/types/api-types"
import { RestaurantCard } from "./restaurant-card"

type User = components["schemas"]["UserResponse"]
type NearbyRestaurantsResponse = components["schemas"]["NearbyRestaurantsResponse"]
type Restaurant = components["schemas"]["Restaurant"]

interface RestaurantsViewProps {
  user?: User | null
}

export function RestaurantsView({ user }: RestaurantsViewProps) {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Finding nearby restaurants...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Nearby Restaurants
          </h1>
          <p className="text-gray-600">
            Find great food options near you
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
            <button
              onClick={fetchNearbyRestaurants}
              className="ml-4 text-red-800 underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        )}

        {restaurants.length === 0 && !error ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No restaurants found nearby</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {restaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}