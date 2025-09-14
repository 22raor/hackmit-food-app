import { NextRequest, NextResponse } from 'next/server'
import { auth } from "@/auth";

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const session = await await auth();
    
    if (!session?.access_token) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const formData = await request.formData()
    
    const backendResponse = await fetch(`${process.env.BACKEND_URL}/restaurants/upload-menu`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      },
      body: formData
    })

    if (!backendResponse.ok) {
      const errorData = await backendResponse.text()
      console.error('Backend upload error:', errorData)
      return NextResponse.json(
        { error: 'Failed to upload menu', details: errorData },
        { status: backendResponse.status }
      )
    }

    const result = await backendResponse.json()
    return NextResponse.json(result)

  } catch (error) {
    console.error('Upload menu API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
