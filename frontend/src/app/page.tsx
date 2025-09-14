"use client"

import { signIn, signOut } from "next-auth/react"
import { useUser } from "@/hooks/useUser"

export default function Home() {
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

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-green-500">
      <div className="text-center text-white">
        <h1 className="text-4xl font-bold mb-8">
          Successfully signed in!
        </h1>

        {error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            Error loading user data: {error}
          </div>
        ) : user ? (
          <div className="bg-white text-gray-900 rounded-lg p-6 shadow-lg">
            <h2 className="text-2xl font-semibold mb-4">User Information</h2>
            <div className="space-y-2 text-left">
              <p><strong>ID:</strong> {user.id}</p>
              <p><strong>Email:</strong> {user.email}</p>
            </div>
          </div>
        ) : (
          <p>Loading user information...</p>
        )}

        <button
          onClick={() => signOut()}
          className="mt-6 rounded-full border border-solid border-white border-opacity-30 transition-colors flex items-center justify-center bg-red-600 hover:bg-red-700 text-white font-medium text-lg h-12 px-8"
        >
          Sign Out
        </button>
      </div>
    </div>
  )
}
