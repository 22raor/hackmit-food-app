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

  useEffect(() => {
    if (session?.access_token) {
      setLoading(true)
      setError(null)

      getCurrentUser(session.access_token)
        .then((userData) => {
          setUser(userData)
        })
        .catch((err) => {
          setError(err.message)
        })
        .finally(() => {
          setLoading(false)
        })
    }
  }, [session?.access_token])

  return {
    user,
    loading: status === "loading" || loading,
    error,
    isAuthenticated: !!session
  }
}