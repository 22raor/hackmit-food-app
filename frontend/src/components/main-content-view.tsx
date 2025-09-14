"use client"

import { useState } from "react"
import { useUserProfile } from "@/hooks/useUserProfile"
import { TasteProfileSetup } from "./taste-profile-setup"
import { LoadingSpinner } from "./ui/loading-spinner"
import { ErrorMessage } from "./ui/error-message"
import { ActionButtons } from "./ui/action-buttons"
import { MobileLayout } from "./ui/mobile-layout"
import { components } from "@/types/api-types"
import Link from "next/link"
import { signOut } from "next-auth/react"

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
    <MobileLayout>
      {/* Header with logout button */}
      <div className="flex justify-between items-center px-8 pt-4 pb-2">
        <div></div> {/* Empty div for spacing */}
        <button
          onClick={() => signOut()}
          className="text-[#555555] text-[14px] hover:text-[#212528] transition-colors"
        >
          Logout
        </button>
      </div>

      <div className="flex-1 px-8 py-6">
        {/* Profile Header */}
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-gray-300 rounded-full mx-auto mb-4"></div>
          <h1 className="text-[32px] font-semibold text-black mb-2">
            {user ? `${user.first_name} ${user.last_name}`.trim() || 'User' : 'User'}
          </h1>
          <p className="text-[#555555] text-base">Welcome to Foodly</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 desktop-two-column gap-4 mb-8">
          <Link href="/restaurants" className="bg-white rounded-[13px] p-6 text-center shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)] hover:shadow-lg transition-shadow">
            <div className="w-12 h-12 bg-[#212528] rounded-full mx-auto mb-3 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="white" className="w-6 h-6">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
            </div>
            <p className="font-semibold text-black">Find Restaurants</p>
          </Link>

          <Link href="/agentic" className="bg-white rounded-[13px] p-6 text-center shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)] hover:shadow-lg transition-shadow block">
            <div className="w-12 h-12 bg-[#212528] rounded-full mx-auto mb-3 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="white" className="w-6 h-6">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
            </div>
            <p className="font-semibold text-black">Agentic Ordering</p>
          </Link>

          <Link href="/scan-menu" className="bg-white rounded-[13px] p-6 text-center shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)] hover:shadow-lg transition-shadow block col-span-2">
            <div className="w-12 h-12 bg-[#212528] rounded-full mx-auto mb-3 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="white" className="w-6 h-6">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
            </div>
            <p className="font-semibold text-black">Scan a Menu</p>
          </Link>
        </div>

        {/* Profile Settings */}
        <div className="space-y-4 mb-8">
          <h2 className="text-[20px] font-semibold text-black mb-4">Profile Settings</h2>

          <button
            onClick={() => setShowTasteSetup(true)}
            className="w-full bg-white rounded-[13px] p-4 flex items-center justify-between shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)] hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center">
              <div className="w-10 h-10 bg-[#f5f6f8] rounded-full mr-4 flex items-center justify-center">
                <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-[#555555]">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <div className="text-left">
                <p className="font-semibold text-black">Taste Preferences</p>
                <p className="text-[#555555] text-sm">Update your flavor profile</p>
              </div>
            </div>
            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-[#555555]">
              <path d="M9 18l6-6-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>


          <div className="w-full bg-white rounded-[13px] p-4 flex items-center justify-between shadow-[0px_4px_4px_0px_rgba(0,0,0,0.08)]">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-[#f5f6f8] rounded-full mr-4 flex items-center justify-center">
                <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-[#555555]">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                </svg>
              </div>
              <div className="text-left">
                <p className="font-semibold text-black">Profile Complete</p>
                <p className="text-[#555555] text-sm">
                  {hasProfile ? 'All set up!' : 'Setup required'}
                </p>
              </div>
            </div>
            <div className={`w-3 h-3 rounded-full ${hasProfile ? 'bg-green-500' : 'bg-red-500'}`}></div>
          </div>
        </div>

        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} title="Error loading user data" />
          </div>
        )}
      </div>
    </MobileLayout>
  )
}
