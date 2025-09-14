"use client"

import { useSession } from "next-auth/react"
import { useUser } from "@/hooks/useUser"
import { AuthFailurePage } from "@/components/auth-failure-page"
import { LandingPage } from "@/components/landing-page"
import { TasteProfileSetup } from "@/components/taste-profile-setup"

export default function Home() {
  const { data: session } = useSession()
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

  // Check if user is new and needs to set up taste profile
  if (session?.is_new_user && user?.id) {
    return (
      <TasteProfileSetup
        userId={user.id}
        onComplete={() => {
          // Force a page reload to refresh the session and user data
          window.location.reload()
        }}
      />
    )
  }

  return <LandingPage />
}
