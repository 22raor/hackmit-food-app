"use client"

import { useSession } from "next-auth/react"
import { useUser } from "@/hooks/useUser"
import { useUserProfile } from "@/hooks/useUserProfile"
import { AuthFailurePage } from "@/components/auth-failure-page"
import { LandingPage } from "@/components/landing-page"
import { TasteProfileSetup } from "@/components/taste-profile-setup"

export default function Home() {
  const { data: session } = useSession()
  const { user, loading: userLoading, error, isAuthenticated } = useUser()
  const { hasProfile, loading: profileLoading } = useUserProfile(user?.id)

  if (userLoading || profileLoading) {
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

  // Check if user needs to set up taste profile by checking if they have one
  // This fixes the endless loop bug for first-time users
  if (user?.id && hasProfile === false) {
    return (
      <TasteProfileSetup
        userId={user.id}
        onComplete={() => {
          // Force a page reload to refresh the user profile data
          window.location.reload()
        }}
      />
    )
  }

  return <LandingPage />
}
