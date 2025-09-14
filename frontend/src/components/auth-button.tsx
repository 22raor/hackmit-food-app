"use client"

import { signIn, signOut, useSession } from "next-auth/react"
import { getCurrentUser } from "@/lib/api"
import { useState } from "react"

export function AuthButton() {
  const { data: session, status } = useSession()
  const [testResult, setTestResult] = useState<string>("")
  const [isTestingToken, setIsTestingToken] = useState(false)

  const testToken = async () => {
    if (!session?.access_token) {
      setTestResult("No access token found in session")
      return
    }

    setIsTestingToken(true)
    setTestResult("")

    try {
      const user = await getCurrentUser(session.access_token)
      setTestResult(`✅ Token works! User: ${user.email} (${user.first_name} ${user.last_name})`)
    } catch (error) {
      setTestResult(`❌ Token failed: ${error instanceof Error ? error.message : String(error)}`)
    } finally {
      setIsTestingToken(false)
    }
  }

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
      <div className="flex flex-col items-end gap-4">
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
            onClick={testToken}
            disabled={isTestingToken}
            className="rounded-full border border-solid border-green-600 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-medium text-sm h-10 px-4"
          >
            {isTestingToken ? "Testing..." : "Test Token"}
          </button>
          <button
            onClick={() => signOut()}
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm h-10 px-4"
          >
            Sign Out
          </button>
        </div>
        {testResult && (
          <div className="text-sm max-w-md text-right">
            {testResult}
          </div>
        )}
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