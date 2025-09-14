"use client"

import { useState } from "react"
import { useUserProfile } from "@/hooks/useUserProfile"
import { TasteProfileSetup } from "./taste-profile-setup"
import { LoadingSpinner } from "./ui/loading-spinner"
import { ErrorMessage } from "./ui/error-message"
import { UserWelcome } from "./profile/user-welcome"
import { ActionButtons } from "./ui/action-buttons"
import { components } from "@/types/api-types"

type User = components["schemas"]["UserResponse"]

interface MainContentViewProps {
  user?: User | null
  error?: string | null
}

export function MainContentView({ user, error }: MainContentViewProps) {
  const { profile, loading: profileLoading, hasProfile, refreshProfile } = useUserProfile(
    user?.id
  )
  const [showTasteSetup, setShowTasteSetup] = useState(false)

  if (profileLoading) {
    return <LoadingSpinner message="Loading your profile..." />
  }

  if (hasProfile === false || showTasteSetup) {
    return (
      <TasteProfileSetup
        userId={user?.id || ""}
        onComplete={() => {
          setShowTasteSetup(false)
          refreshProfile()
        }}
      />
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          HackMIT Food App
        </h1>

        {error ? (
          <ErrorMessage message={error} title="Error loading user data" />
        ) : user ? (
          <UserWelcome user={user} profile={profile} />
        ) : (
          <div className="bg-white rounded-lg p-6 shadow-lg mb-6">
            <p className="text-gray-900">Loading user information...</p>
          </div>
        )}

        <ActionButtons
          hasProfile={hasProfile === true}
          onUpdatePreferences={() => setShowTasteSetup(true)}
        />
      </div>
    </div>
  )
}