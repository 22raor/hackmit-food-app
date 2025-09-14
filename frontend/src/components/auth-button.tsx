"use client"

import { signIn, signOut, useSession } from "next-auth/react"

export function AuthButton() {
  const { data: session, status } = useSession()

  if (status === "loading") {
    return (
      <button
        disabled
        className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] bg-gray-100 dark:bg-gray-800 text-gray-400 font-medium text-sm h-10 px-4"
      >
        Loading...
      </button>
    )
  }

  if (session) {
    return (
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          {session.user?.image && (
            <img
              src={session.user.image}
              alt="Profile"
              className="w-8 h-8 rounded-full"
            />
          )}
          <span className="text-sm">
            Welcome, {session.user?.name || session.user?.email}!
          </span>
        </div>
        <button
          onClick={() => signOut()}
          className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm h-10 px-4"
        >
          Sign Out
        </button>
      </div>
    )
  }

  return (
    <button
      onClick={() => signIn("google")}
      className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm h-10 px-6"
    >
      Sign in with Google
    </button>
  )
}