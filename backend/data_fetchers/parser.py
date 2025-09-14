import re
import json
import os
from gmap import enrich_with_maps, get_popular_items_info
from beli import Beli
from dotenv import load_dotenv
from doordash_scrape import get_nearby_restaurants, process_doordash_url
import asyncio


async def get_some_restaurants(cap = 10):
    load_dotenv("../backend/.env")

    USER_EMAIL = os.getenv("BELI_USER_EMAIL")
    USER_PASSWORD = os.getenv("BELI_USER_PASSWORD")
    USER_ID = os.getenv("USER_ID")
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    # print(API_KEY)

    beli = Beli(email=USER_EMAIL, password=USER_PASSWORD, user_id=USER_ID)

    # rests = (await get_nearby_restaurants())[:cap]
    # print('found ' + str(len(rests)) + ' restaurants')

    rests = ['https://www.doordash.com/store/hei-la-moon-restaurant-boston-45774', 'https://www.doordash.com/store/la-perle-caribbean-restaurant-everett-2804730', 'https://www.doordash.com/store/pai-kin-kao-thai-restaurant-cambridge-31557551']
    for restaurant_url in rests:
        print("processing " + restaurant_url)
        success, data = await process_doordash_url(restaurant_url)
        if success:
            status, place_id, reviews = enrich_with_maps(data["address"], data["latitude"], data["longitude"], API_KEY)
            # print(status)
            if status:
                data["place_id"] = place_id
                data["reviews"] = reviews
                # print(reviews)

            belstatus, beli_id, top_items = beli.get_complete_res_info(
                data["name"],
                data["latitude"],
                data["longitude"],
                f"{data['city'], data['state']}",
            )
            if belstatus:
                data["beli_id"] = beli_id
                data["top_items"] = top_items
            
            # write data to res.txt
            with open('../backend/food_info/processed/' + data['name'] + '.json', 'w') as file:
                json.dump(data, file)

            # print(data)

if __name__ == '__main__':
    asyncio.run(get_some_restaurants(cap=30))
