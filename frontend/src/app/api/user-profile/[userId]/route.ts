import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/auth"
import { components } from "@/types/api-types"

type TasteProfileResponse = components["schemas"]["TasteProfileResponse"]
type UpdateTasteProfile = components["schemas"]["UpdateTasteProfile"]

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string }> }
) {
  try {
    const session = await auth()

    if (!session?.access_token) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const { userId } = await params
    const response = await fetch(`${API_BASE_URL}/user_profile/${userId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      },
    })

    if (response.status === 404) {
      return NextResponse.json({ error: "Profile not found" }, { status: 404 })
    }

    if (!response.ok) {
      const errorData = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}`, details: errorData },
        { status: response.status }
      )
    }

    const data: TasteProfileResponse = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error("Error fetching user profile:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string }> }
) {
  try {
    const session = await auth()

    if (!session?.access_token) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body: UpdateTasteProfile = await request.json()
    const { userId } = await params

    const response = await fetch(`${API_BASE_URL}/user_profile/${userId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.access_token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      const errorData = await response.text()
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}`, details: errorData },
        { status: response.status }
      )
    }

    const data: TasteProfileResponse = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error("Error updating user profile:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}