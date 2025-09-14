
import re
import json
import os
from gmap import enrich_with_maps
from beli import Beli
from dotenv import load_dotenv


def get_nested_val(data_dict, keys, default=[]):
    temp_dict = data_dict
    for key in keys:
        if isinstance(temp_dict, dict):
            temp_dict = temp_dict.get(key)
        else:
            return default
    return temp_dict

def extract_json_from_html(html_content):
    # Regex to find the line containing the restaurant data
    matches = re.search(r'self\.__next_f\.push\(\[1,\s*"2f:(.*)\]\)', html_content, re.DOTALL)
    # matches = re.search(r' self\.__next_f\.push\(\[1, "2f:', html_content)
    if not matches:
        print("No match found")
        return False, None
    raw = matches.group(0).strip()
    raw = raw.split("</script>")[0].strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return False, None

    json_like = raw[start:end+1]
    raw_json = json_like.encode("utf-8").decode("unicode_escape")
    raw_json = raw_json.replace("undefined", "null")
    open("out.txt", "w").write(raw_json)
    try:
        data = json.loads(raw_json)
        print("Successfully parsed JSON")
        data = data["platformProps"]["additionalPlatformProps"]["apolloCacheData"][0]["data"]["storepageFeed"]
        return True, data
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return False, None


def json_extract(data):
    store_header = data.get('storeHeader', {})
    mx_info = data.get('mxInfo', {})

    restaurant_info = {
        "id": get_nested_val(store_header, ['id'], "N/A"),
        "name": get_nested_val(store_header, ['name'], "N/A"),
        "average_rating": get_nested_val(store_header, ['ratings', 'averageRating']),
        "review_count": get_nested_val(store_header, ['ratings', 'numRatingsDisplayString']),
        "image_url": get_nested_val(store_header, ['coverImgUrl'], "N/A"),
        "address": get_nested_val(store_header, ['address', 'displayAddress'], "N/A"),
        "latitude": get_nested_val(store_header, ['address', 'lat'], "N/A"),
        "longitude": get_nested_val(store_header, ['address', 'lng'], "N/A"),
        "city": get_nested_val(store_header, ['address', 'city'], "N/A"),
        "state": get_nested_val(store_header, ['address', 'state'], "N/A"),
        "price_range": get_nested_val(store_header, ['priceRangeDisplayString'], "N/A"),

        "tags": [tag.get('name') for tag in store_header.get('businessTags', [])],
        "other_info": {
                "description": get_nested_val(store_header, ['storeBio'], "N/A"),
                "phone_number": get_nested_val(mx_info, ['phoneno'], "N/A"),
                "website": get_nested_val(mx_info, ['website'], "N/A"),
                "delivery_time": get_nested_val(store_header, ['deliveryTimeLayout', 'title'], "N/A"),
                "pickup_time": get_nested_val(store_header, ['pickupTimeLayout', 'title'], "N/A")
            },
        "menu_items": []
        }

    item_lists = data.get('itemLists', [])
    for category in item_lists:
        category_name = category.get('name', 'Uncategorized')
        items = category.get('items', [])
        for item in items:
            menu_item = {
                "name": item.get('name', 'N/A'),
                "description": item.get('description', ''),
                "price": item.get('displayPrice', 'N/A').replace('$$', '$'),
                "image_url": item.get('imageUrl', None),
                "category": category_name,
                "rating": item.get('ratingDisplayString'),
                "most_ordered": False
            }
            restaurant_info["menu_items"].append(menu_item)

    most_ordered_items = []
    for mitem in restaurant_info["menu_items"]:
        if mitem["category"] == "Most Ordered":
            most_ordered_items.append(mitem["name"])
        if mitem["name"] in most_ordered_items:
            mitem["most_ordered"] = True

    # Sort menu items by price in ascending order
    restaurant_info["menu_items"] = [item for item in restaurant_info["menu_items"] if item["category"] != "Most Ordered"]

    return restaurant_info


if __name__ == '__main__':
    all_restaurants_data = []
    load_dotenv()

    USER_EMAIL = os.getenv("USER_EMAIL")
    USER_PASSWORD = os.getenv("USER_PASSWORD")
    USER_ID = os.getenv("USER_ID")
    API_KEY = os.getenv("API_KEY")

    beli = Beli(email=USER_EMAIL, password=USER_PASSWORD, user_id=USER_ID)


    files = os.listdir("./data")
    for file in files:
        f = open("./data/" + file, 'r').read()
        fname = file.split(".")[0]
        success, json_data = extract_json_from_html(f)
        if success:
            data = json_extract(json_data)
            status, place_id, reviews = enrich_with_maps(data["address"], data["latitude"], data["longitude"], API_KEY)
            if status:
                data["place_id"] = place_id
                data["reviews"] = reviews

            belstatus, beli_id, top_items = beli.get_complete_res_info(data["name"], data["latitude"], data["longitude"], f"{data['city'], data['state']}")
            if belstatus:
                data["beli_id"] = beli_id
                data["top_items"] = top_items

            open(f"./processed/{fname}.json", 'w').write(json.dumps(data))
