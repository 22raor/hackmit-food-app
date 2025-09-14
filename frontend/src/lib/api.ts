import { components } from "../types/api-types"

type UserResponse = components["schemas"]["UserResponse"]
type TasteProfileResponse = components["schemas"]["TasteProfileResponse"]
type UpdateTasteProfile = components["schemas"]["UpdateTasteProfile"]

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000"

export async function getCurrentUser(accessToken: string): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch user info: ${response.status} ${response.statusText}`)
  }

  return await response.json()
}

export async function getUserProfile(accessToken: string, userId: string): Promise<TasteProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/user_profile/${userId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch user profile: ${response.status} ${response.statusText}`)
  }

  return await response.json()
}

export async function updateUserProfile(accessToken: string, userId: string, profile: UpdateTasteProfile): Promise<TasteProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/user_profile/${userId}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile)
  })

  if (!response.ok) {
    throw new Error(`Failed to update user profile: ${response.status} ${response.statusText}`)
  }

  return await response.json()
}