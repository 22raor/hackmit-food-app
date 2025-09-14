"use client"

import { MobileLayout } from "@/components/ui/mobile-layout"
import { useUser } from "@/hooks/useUser"
import { AuthFailurePage } from "@/components/auth-failure-page"
import VapiWidget from "@/components/vapi-widget"
import Link from "next/link"
import { signOut } from "next-auth/react"

export default function AgenticPage() {
  const { isAuthenticated, loading, user } = useUser()

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
          <h1 className="text-[20px] font-semibold text-black">Agentic Ordering</h1>
          <button
            onClick={() => signOut()}
            className="text-[#555555] text-[14px] hover:text-[#212528] transition-colors"
          >
            Logout
          </button>
        </div>

        <VapiWidget
          apiKey={process.env.NEXT_PUBLIC_VAPI_API_KEY || ""}
          assistantId="fde8b491-8699-46aa-95ee-d0c233a26bb2"
          userId={user?.id}
        />
      </div>
    </MobileLayout>
  )
}