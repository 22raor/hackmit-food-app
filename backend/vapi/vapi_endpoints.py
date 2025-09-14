from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, Request
from typing import Dict, List, Any, Optional
import json
from food_info.info_api import get_restaurant_by_id, RESTAURANTS_LIST_CACHE


router = APIRouter(prefix="/vapi", tags=["vapi"])

# In-memory cart storage using hashmap
USER_CARTS: Dict[str, List[Dict[str, Any]]] = {}


class GetUserCartRequest(BaseModel):
    user_id: str


class AddItemToCartRequest(BaseModel):
    item_id: int
    user_id: Optional[str] = None


class GetRestaurantInfoRequest(BaseModel):
    restaurant_id: str


class ToolCallFunction(BaseModel):
    name: str
    arguments: str | dict


class ToolCall(BaseModel):
    id: str
    function: ToolCallFunction


class Message(BaseModel):
    toolCalls: list[ToolCall]


class VapiRequest(BaseModel):
    message: Message


@router.post("/item-cart")
async def get_user_cart(request: VapiRequest):
    """Get Items currently in the user cart for the session."""
    my_tool_call = None
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getRestaurantInfo":
            my_tool_call = tool_call
            break
    if not my_tool_call:
        raise HTTPException(status_code=400, detail="Invalid tool call")
    args = my_tool_call.function.arguments
    if isinstance(args, str):
        args = json.loads(args)

    user_id = args.get("user_id")
    item_id = args.get("item_id")
    if not user_id or not item_id:
        raise HTTPException(status_code=400, detail="Invalid arguments")

    if user_id not in USER_CARTS:
        USER_CARTS[user_id] = []

    return {
        "results": [
            {
                "toolCallId": my_tool_call.id,
                "result": {
                    "user_id": user_id,
                    "cart_items": USER_CARTS[user_id],
                    "total_items": len(USER_CARTS[user_id]),
                },
            }
        ]
    }


@router.post("/user_cart")
async def add_item_to_cart(request: VapiRequest):
    """Allow the user to add items to their cart."""
    my_tool_call = None
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getRestaurantInfo":
            my_tool_call = tool_call
            break
    if not my_tool_call:
        raise HTTPException(status_code=400, detail="Invalid tool call")
    args = my_tool_call.function.arguments
    if isinstance(args, str):
        args = json.loads(args)
    user_id = args.get("user_id")
    item_id = args.get("item_id")
    if not user_id or not item_id:
        raise HTTPException(status_code=400, detail="Invalid arguments")

    if user_id not in USER_CARTS:
        USER_CARTS[user_id] = []

    # Find the item across all restaurants to get item details
    item_details = None
    restaurant_name = None

    for restaurant_data in [
        get_restaurant_by_id(r["id"])
        for r in RESTAURANTS_LIST_CACHE
        if get_restaurant_by_id(r["id"])
    ]:
        if restaurant_data and "menu_items" in restaurant_data:
            for item in restaurant_data["menu_items"]:
                if item.get("id") == item_id:
                    item_details = item
                    restaurant_name = restaurant_data.get("name")
                    break
        if item_details:
            break

    if not item_details:
        raise HTTPException(
            status_code=404, detail=f"Menu item with ID {item_id} not found"
        )

    # Add item to cart with restaurant context
    cart_item = {
        "item_id": item_id,
        "name": item_details.get("name"),
        "price": item_details.get("price"),
        "description": item_details.get("description"),
        "restaurant_name": restaurant_name,
        "quantity": 1,
    }

    # Check if item already exists in cart and increment quantity
    existing_item = None
    for existing in USER_CARTS[user_id]:
        if existing.get("item_id") == item_id:
            existing_item = existing
            break

    if existing_item:
        existing_item["quantity"] += 1
    else:
        USER_CARTS[user_id].append(cart_item)

    return {
        "results": [
            {
                "toolCallId": my_tool_call.id,
                "result": {
                    "message": f"Added {item_details.get('name')} to cart",
                    "cart_items": USER_CARTS[user_id],
                    "total_items": len(USER_CARTS[user_id]),
                },
            }
        ]
    }


@router.post("/restaurant-by-id")
async def get_restaurant_info(request: VapiRequest):
    """Get full information about restaurant - menu items, reviews, top items, other information"""
    my_tool_call = None
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getRestaurantInfo":
            my_tool_call = tool_call
            break
    if not my_tool_call:
        raise HTTPException(status_code=400, detail="Invalid tool call")
    args = my_tool_call.function.arguments
    if isinstance(args, str):
        args = json.loads(args)
    restaurant_id = args.get("restaurant_id")
    print(restaurant_id)
    if not restaurant_id:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant_data = get_restaurant_by_id(restaurant_id)

    if not restaurant_data:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {"results": [{"toolCallId": my_tool_call.id, "result": restaurant_data}]}


@router.post("/restaurants")
async def get_restaurant_list(request: VapiRequest):
    """Fetch restaurants the user has access to order from"""
    my_tool_call = None
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getRestaurantList":
            my_tool_call = tool_call
            break
    print(my_tool_call)

    if not my_tool_call:
        return {"results": [{"result": "failure"}]}

    return {
        "results": [
            {
                "toolCallId": my_tool_call.id,
                "result": {
                    # 'restaurants': [{"name": r["name"], "id": r["id"], "tags": r["tags"]} for r in RESTAURANTS_LIST_CACHE],
                    "restaurants": RESTAURANTS_LIST_CACHE,
                    "total_count": len(RESTAURANTS_LIST_CACHE),
                },
            }
        ]
    }
