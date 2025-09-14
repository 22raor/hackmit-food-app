"use client"

import { MobileLayout } from "./ui/mobile-layout"
import Link from "next/link"
import { signOut } from "next-auth/react"

export function LandingPage() {
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

      <div className="flex-1 flex flex-col items-center justify-center px-8 py-8">
        {/* App Title */}
        <div className="text-center mb-12">
          <h1 className="text-[48px] font-bold text-black leading-[52px] mb-4">
            Foodly
          </h1>
          <p className="text-[#555555] text-[16px]">
            Discover your perfect meal
          </p>
        </div>

        {/* Main Action Buttons */}
        <div className="w-full max-w-sm space-y-4">
          <Link href="/restaurants" className="block w-full">
            <button className="w-full h-[56px] bg-[#212528] text-white rounded-[13px] font-medium text-[16px] hover:bg-[#313538] transition-colors flex items-center justify-center gap-3">
              <svg viewBox="0 0 24 24" fill="white" className="w-6 h-6">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
              </svg>
              Local Restaurants
            </button>
          </Link>

          <Link href="/agentic" className="block w-full">
            <button className="w-full h-[56px] border border-[#e6e6e6] text-[#212528] rounded-[13px] font-medium text-[16px] hover:border-[#212528] transition-colors flex items-center justify-center gap-3">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
              Agentic Ordering
            </button>
          </Link>

          <Link href="/profile" className="block w-full">
            <button className="w-full h-[56px] border border-[#e6e6e6] text-[#212528] rounded-[13px] font-medium text-[16px] hover:border-[#212528] transition-colors flex items-center justify-center gap-3">
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
              Profile
            </button>
          </Link>
        </div>
      </div>
    </MobileLayout>
  )
}