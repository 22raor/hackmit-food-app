"use client"

import { signIn } from "next-auth/react"
import { useState } from "react"

export function AuthFailurePage() {
  const [showSignup, setShowSignup] = useState(false)

  const StatusBar = () => (
    <div className="flex justify-between items-center h-[54px] px-4 bg-[#f5f6f8]">
      <div className="w-[138px] flex justify-center">
        <span className="font-semibold text-[17px] text-black">9:41</span>
      </div>
      <div className="w-[143px]"></div>
    </div>
  )

  const GoogleSignInButton = () => (
    <button
      onClick={() => signIn("google")}
      className="bg-white border border-[#e6e6e6] rounded-[13px] h-12 w-full flex items-center justify-center mb-6 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="w-[27px] h-[27px] mr-4">
        <svg viewBox="0 0 24 24" className="w-full h-full">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
      </div>
      <span className="text-[#555555] text-base font-normal">Sign in with Google</span>
    </button>
  )

  const SignupForm = () => (
    <div className="space-y-6 mt-8">
      <div className="text-center mb-6">
        <span className="text-[#555555] text-base">or</span>
        <div className="flex items-center mt-2">
          <div className="flex-1 h-px bg-[#e6e6e6]"></div>
          <div className="flex-1 h-px bg-[#e6e6e6] ml-4"></div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="relative">
          <label className="block text-sm font-semibold text-black mb-1">Name*</label>
          <input
            type="text"
            className="w-full h-12 bg-white border border-[#e6e6e6] rounded-[13px] px-4 text-base placeholder-[#555555] focus:outline-none focus:border-[#212528]"
            placeholder="Enter your name"
          />
        </div>

        <div className="relative">
          <label className="block text-sm font-semibold text-black mb-1">Email*</label>
          <input
            type="email"
            className="w-full h-12 bg-white border border-[#e6e6e6] rounded-[13px] px-4 text-base placeholder-[#555555] focus:outline-none focus:border-[#212528]"
            placeholder="Enter your email"
          />
        </div>

        <div className="relative">
          <label className="block text-sm font-semibold text-black mb-1">Password*</label>
          <input
            type="password"
            className="w-full h-12 bg-white border border-[#e6e6e6] rounded-[13px] px-4 text-base placeholder-[#555555] focus:outline-none focus:border-[#212528]"
            placeholder="Enter your password"
          />
        </div>
      </div>

      <button className="w-full h-[42px] bg-[#212528] text-white rounded-[13px] font-normal text-base hover:bg-[#313538] transition-colors">
        Create Account
      </button>

      <div className="text-center">
        <span className="text-[#555555] text-[11px]">Already have an account? </span>
        <button
          onClick={() => setShowSignup(false)}
          className="text-black text-[11px] underline hover:no-underline"
        >
          Login Here
        </button>
      </div>
    </div>
  )

  return (
    <div className="mobile-container">
      <StatusBar />

      <div className="px-14 py-8 flex flex-col items-center min-h-[calc(100vh-54px)]">
        <div className="flex-1 flex flex-col justify-center w-full max-w-[281px]">
          <h1 className="text-[40px] font-bold text-black leading-[45px] mb-8 text-left">
            Welcome to Foodly
          </h1>

          <GoogleSignInButton />

          {showSignup && <SignupForm />}

          {!showSignup && (
            <div className="mt-auto mb-8">
              <button
                onClick={() => setShowSignup(true)}
                className="w-full h-[42px] bg-[#212528] text-white rounded-[13px] font-normal text-base hover:bg-[#313538] transition-colors"
              >
                Create Account
              </button>
            </div>
          )}
        </div>

        <div className="w-[115px] h-[5px] bg-[#212528] rounded-[25px] mt-auto mb-4"></div>
      </div>
    </div>
  )
}