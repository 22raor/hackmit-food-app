import json
import requests

def get_restaurant_details(address, lat, lng, api_key, radius_meters=1000):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id" # Specify the fields you want
    }

    data = {
        "textQuery": address,
        "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": lat,
                            "longitude": lng
                        },
                        "radius": radius_meters
                    }
                }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        # Process the result
        places = result['places']
        if len(places):
            place = places[0]['id']
            return True, place
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return False, ""


def get_popular_items_info(place_id, api_key):
    """
    Retrieves reviews and photos from the Places API (New) to infer popular items.
    """


    url = f"https://places.googleapis.com/v1/places/{place_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "reviews"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        resp =  response.json()
        reviews = resp.get('reviews', [])
        return [review["text"]["text"].strip() for review in reviews]
    else:
        print(f"Error getting place details: {response.status_code}")
        print(response.text)
        return None

def enrich_with_maps(address, lat, lng, api_key):
    success, place_id = get_restaurant_details(address, lat, lng, api_key)
    if success:
        popular_items = get_popular_items_info(place_id, api_key)
        return True, place_id, popular_items
    else:
        return False, "", []
