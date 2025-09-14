import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { components } from "@/types/api-types";

type NearbyRestaurantsResponse = components["schemas"]["NearbyRestaurantsResponse"];

const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
    request: NextRequest
) {
    try {
        const session = await auth();

        if (!session?.access_token) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const response = await fetch(`${API_BASE_URL}/restaurants`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json',
            },
        });
      console.log(response);
      console.log(session);

        if (!response.ok) {
            const errorData = await response.text();
            return NextResponse.json(
                { error: `Backend error: ${response.status} ${response.statusText}`, details: errorData },
                { status: response.status }
            );
        }

        const data: any = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error("Error fetching nearby restaurants:", error);
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        );
    }
}
