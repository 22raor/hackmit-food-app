import { NextResponse, NextRequest } from "next/server";
import { auth } from "@/auth";
import { components } from "@/types/api-types";

type RecomomendationRequest = components["schemas"]["RecommendationRequest"];
type RecommendationResponse = components["schemas"]["RecommendationResponse"];

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(
    request: NextRequest,
    { params }: { params: Promise<{ restaurantId: string }> }
    ) {
    try {
        const session = await auth();
        if (!session?.access_token) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { restaurantId } = await params;
        const body: RecomomendationRequest = await request.json();
        const response = await fetch(`${API_BASE_URL}/recs/${restaurantId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.text();
            return NextResponse.json(
                { error: `Backend error: ${response.status} ${response.statusText}`, details: errorData },
                { status: response.status }
            );
        }

        const data: RecommendationResponse = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        );
    }
}