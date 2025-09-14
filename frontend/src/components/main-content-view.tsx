"use client"

import { useState } from "react"
import { signOut, useSession } from "next-auth/react"
import { useUserProfile } from "@/hooks/useUserProfile"
import { TasteProfileSetup } from "./taste-profile-setup"
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
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading your profile...</p>
        </div>
      </div>
    )
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
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            Error loading user data: {error}
          </div>
        ) : user ? (
          <div className="bg-white text-gray-900 rounded-lg p-6 shadow-lg mb-6">
            <h2 className="text-2xl font-semibold mb-4">Welcome back, {user.first_name}!</h2>
            {profile && (
              <div className="space-y-3 text-left">
                <p className="text-gray-600">Profile configured with:</p>
                {profile.profile.dietary_restrictions.length > 0 ||
                 profile.profile.cuisine_preferences.length > 0 ||
                 profile.profile.liked_foods.length > 0 ? (
                  <ul className="text-sm space-y-1">
                    {profile.profile.dietary_restrictions.length > 0 && (
                      <li>• {profile.profile.dietary_restrictions.length} dietary restrictions</li>
                    )}
                    {profile.profile.cuisine_preferences.length > 0 && (
                      <li>• {profile.profile.cuisine_preferences.length} cuisine preferences</li>
                    )}
                    {profile.profile.liked_foods.length > 0 && (
                      <li>• {profile.profile.liked_foods.length} liked foods</li>
                    )}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">No dietary restrictions, cuisine preferences, or liked foods set</p>
                )}

                {profile.profile.flavor_profile && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-gray-600 mb-2">Flavor Profile:</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex justify-between">
                        <span>Spicy:</span>
                        <span className="font-medium">{profile.profile.flavor_profile.spicy_tolerance}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sweet:</span>
                        <span className="font-medium">{profile.profile.flavor_profile.sweet_preference}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Salty:</span>
                        <span className="font-medium">{profile.profile.flavor_profile.salty_preference}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sour:</span>
                        <span className="font-medium">{profile.profile.flavor_profile.sour_preference}/10</span>
                      </div>
                      <div className="flex justify-between col-span-2">
                        <span>Umami:</span>
                        <span className="font-medium">{profile.profile.flavor_profile.umami_preference}/10</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg p-6 shadow-lg mb-6">
            <p className="text-gray-900">Loading user information...</p>
          </div>
        )}

        <div className="flex space-x-4">
          {hasProfile && (
            <button
              onClick={() => setShowTasteSetup(true)}
              className="rounded-full border border-solid border-blue-600 transition-colors flex items-center justify-center bg-white hover:bg-blue-50 text-blue-600 font-medium text-lg h-12 px-8"
            >
              Update Preferences
            </button>
          )}
          <button
            onClick={() => signOut()}
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-red-600 hover:bg-red-700 text-white font-medium text-lg h-12 px-8"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  )
}