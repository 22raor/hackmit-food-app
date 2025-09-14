"use client"

import { useUser } from "@/hooks/useUser"
import { AuthFailurePage } from "@/components/auth-failure-page"
import { RestaurantsView } from "@/components/restaurants-view"

export default function RestaurantsPage() {
  const { user, loading, error, isAuthenticated } = useUser()

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

  return <RestaurantsView user={user} />
}