"use client"

import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"
import { getCurrentUser } from "../lib/api"
import { components } from "../types/api-types"

type User = components["schemas"]["UserResponse"]

export function useUser() {
  const { data: session, status } = useSession()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    if (status === "loading") {
      return
    }

    if (session?.access_token) {
      setLoading(true)
      setError(null)

      getCurrentUser(session.access_token)
        .then((userData) => {
          setUser(userData)
          setIsAuthenticated(true)
        })
        .catch((err) => {
          // If we get a 401 or similar auth error, treat as unauthenticated
          if (err.message.includes('401') || err.message.includes('Unauthorized')) {
            setIsAuthenticated(false)
            setUser(null)
          } else {
            setError(err.message)
            setIsAuthenticated(true) // Still authenticated, just an API error
          }
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setIsAuthenticated(false)
      setUser(null)
      setError(null)
    }
  }, [session?.access_token, status])

  return {
    user,
    loading: status === "loading" || loading,
    error,
    isAuthenticated
  }
}