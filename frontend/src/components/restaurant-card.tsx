"use client"

import { components } from "@/types/api-types"

interface RestaurantCardProps {
  restaurant: any
  onClick?: () => void
}

export function RestaurantCard({ restaurant, onClick }: RestaurantCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
      onClick={onClick}
    >
      {restaurant.image_url && (
        <img
          src={restaurant.image_url}
          alt={restaurant.name}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {restaurant.name}
        </h3>

        <div className="flex items-center justify-between mb-2">
          {restaurant.rating && (
            <div className="flex items-center">
              <span className="text-yellow-400">★</span>
              <span className="ml-1 text-gray-700">{restaurant.rating}</span>
            </div>
          )}
          <span className="text-gray-600 font-medium">{restaurant.price_range}</span>
        </div>

        <p className="text-gray-600 text-sm mb-3">
          {restaurant.address}
        </p>
        <p className="text-gray-500 text-xs mb-3">
          {restaurant.city}, {restaurant.state} {restaurant.zip_code}
        </p>

        {restaurant.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {restaurant.tags.map((tag: String, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
