import re
import json
import asyncio
from playwright.async_api import async_playwright
import random
import sys
import random

def get_nested_val(data_dict, keys, default=None):
    temp_dict = data_dict
    for key in keys:
        if isinstance(temp_dict, dict):
            temp_dict = temp_dict.get(key)
        else:
            return default
    return temp_dict


async def get_nearby_restaurants():
    html_content = await get_doordash_html('https://www.doordash.com/restaurants-near-me/')  # is loc passed in headless? ignore for now

    if not html_content:
        return []

    matches = re.findall(r'href="(/store[^"]+)"', html_content)
    links = ["https://www.doordash.com" + m for m in matches]
    return list(set(links))


def extract_json_from_html(html_content):
    matches = re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', html_content, re.DOTALL)

    restaurant_data = None
    for json_str in matches:
        try:
            data = json.loads(json_str)
            if data.get('@type') == 'Restaurant':
                restaurant_data = data
                break
        except json.JSONDecodeError:
            continue

    if not restaurant_data:
        return False, None

    menu_page_items = []
    start_idx = 0
    while True:
        idx = html_content.find('\\\"__typename\\\":\\\"MenuPageItemList\\\"', start_idx)
        if idx == -1:
            break

        brace_start = html_content.rfind('{', 0, idx)
        if brace_start == -1:
            break

        depth = 0
        brace_end = None
        for j in range(brace_start, len(html_content)):
            if html_content[j] == '{':
                depth += 1
            elif html_content[j] == '}':
                depth -= 1
                if depth == 0:
                    brace_end = j + 1
                    break

        if brace_end:
            raw = html_content[brace_start:brace_end]
            try:
                parsed = json.loads(raw.encode().decode("unicode_escape"))
                if parsed.get("__typename") == "MenuPageItemList":
                    menu_page_items.append(parsed)
            except Exception:
                pass

        start_idx = idx + 1

    restaurant_data["menuPageItemLists"] = menu_page_items
    # print(menu_page_items)
    return True, restaurant_data




def json_extract(data):
    address = data.get('address', {})
    aggregate_rating = data.get('aggregateRating', {})

    restaurant_info = {
        "id": f"{random.randint(100000, 999999)}" , #random 6 digit int
        "name": data.get('name', "N/A"),
        "average_rating": aggregate_rating.get('ratingValue'),
        "review_count": f"({aggregate_rating.get('reviewCount')}+)",
        "image_url": get_nested_val(data, ['image', 1], "N/A"),
        "address": f"{address.get('streetAddress', 'N/A')}, {address.get('addressLocality', 'N/A')}, {address.get('addressRegion', 'N/A')} {address.get('postalCode', 'N/A')}, {address.get('addressCountry', 'N/A')}",
        "latitude": get_nested_val(data, ['geo', 'latitude']),
        "longitude": get_nested_val(data, ['geo', 'longitude']),
        "city": address.get('addressLocality', "N/A"),
        "state": address.get('addressRegion', "N/A"),
        "price_range": data.get('priceRange', "N/A"),
        "tags": data.get('servesCuisine', []),
        "other_info": {
            "description": None,
            "phone_number": data.get('telephone'),
            "website": data.get('url')
        },
        "menu_items": []
    }

    for parsed in data.get("menuPageItemLists", []):
        category_name = parsed.get('name', 'Uncategorized')
        for item in parsed.get('items', []):
            # print(item)
            menu_item = {
                "name": item.get('name', 'N/A'),
                "description": item.get('description', ''),
                "price": item.get('displayPrice', '$N/A')[1:],
                "image_url": item.get('imageUrl', None),
                "category": category_name,
                "rating": item.get('ratingDisplayString', 'N/A'),
                "most_ordered": False
            }
            restaurant_info["menu_items"].append(menu_item)

    return restaurant_info


async def get_doordash_html(url: str) -> str:
    # user_agents = [
    #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    #     # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    #     # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    #     # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    #     # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    #     # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76",
    #     # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/108.0"
    # ]
    user_agents = [
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/108.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/107.0 Mobile/15E148",
        # "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.128 Mobile Safari/537.36",
    ]
    random_user_agent = random.choice(user_agents)
    print(random_user_agent)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=random_user_agent)
            page = await context.new_page()

            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            content = await page.content()

            await browser.close()
            return content
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None

async def process_doordash_url(url, mock = False):
    """
    Fetches HTML from a given URL, extracts JSON data, and prints the result.
    """
    print("Processing " + url)
    if mock:
        with open('out.txt', 'r') as file:
            html_content = file.read()
    else:
        delay = random.uniform(1, 3)
        print(f"waiting for {delay} seconds...")
        await asyncio.sleep(delay)
        html_content = await get_doordash_html(url)

    if not html_content:
        print(f"Failed to get HTML content from {url}.")
        return

    success, json_data = extract_json_from_html(html_content)
    if success:
        parsed_data = json_extract(json_data)
        return True, parsed_data
    else:
        print(f"Failed to extract and parse JSON from {url}.")

async def main():

    doordash_url = "https://www.doordash.com/store/new-moon-villa-restaurant-boston-885394/"
    
    await process_doordash_url(doordash_url, mock = True)

if __name__ == '__main__':
    asyncio.run(main())
