"use client"

import { useEffect, useState } from "react"
import { components } from "../types/api-types"

type TasteProfileResponse = components["schemas"]["TasteProfileResponse"]

export function useUserProfile(userId: string | undefined) {
  const [profile, setProfile] = useState<TasteProfileResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasProfile, setHasProfile] = useState<boolean | null>(null)

  useEffect(() => {
    if (userId) {
      setLoading(true)
      setError(null)

      fetch(`/api/user-profile/${userId}`)
        .then(async (response) => {
          if (response.status === 404) {
            setHasProfile(false)
            return
          }
          if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.error || "Failed to fetch profile")
          }
          const profileData = await response.json()
          setProfile(profileData)
          setHasProfile(true)
        })
        .catch((err) => {
          setError(err.message)
        })
        .finally(() => {
          setLoading(false)
        })
    }
  }, [userId])

  const refreshProfile = async () => {
    if (userId) {
      try {
        const response = await fetch(`/api/user-profile/${userId}`)
        if (response.status === 404) {
          setHasProfile(false)
          return
        }
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || "Failed to fetch profile")
        }
        const profileData = await response.json()
        setProfile(profileData)
        setHasProfile(true)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch profile")
      }
    }
  }

  return {
    profile,
    loading,
    error,
    hasProfile,
    refreshProfile
  }
}