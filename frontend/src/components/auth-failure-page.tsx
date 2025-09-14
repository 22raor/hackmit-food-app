"use client"

import { signIn } from "next-auth/react"

export function AuthFailurePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          HackMIT Food App
        </h1>
        <button
          onClick={() => signIn("google")}
          className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-medium text-lg h-12 px-8"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  )
}