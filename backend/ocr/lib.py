import os
import base64
from groq import Groq
# from google.cloud import vision
from dotenv import load_dotenv

# from .user_profile.profile_api import MOCK_PROFILES_DB


# Load environment variables from a .env file
load_dotenv("../.env")

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_fetchers.beli import Beli
from data_fetchers.gmap import get_popular_items_info

from data_fetchers.types import OtherInfo, RestaurantInfo, MenuItem, BeliTopItem
import json


# Note: The original script had a google.genai client initialization here.
# It's kept for context but not used if you're only calling the Groq function.
# try:
#     from google import genai
#     from google.genai import types
#     # The client gets the API key from the environment variable `GEMINI_API_KEY`.
#     genai_client = genai.Client()
# except ImportError:
#     print("Google GenAI libraries not found, Gemini function will not be available.")
#     genai_client = None


# def detect_text_from_image(image_path):
#     """Detects text in an image using Google Cloud Vision API."""
#     client = vision.ImageAnnotatorClient()

#     with open(image_path, "rb") as image_file:
#         content = image_file.read()

#     image = vision.Image(content=content)
#     response = client.document_text_detection(image=image)
    
#     if response.error.message:
#         raise Exception(f"{response.error.message}")

#     return response.full_text_annotation.text

# def detect_with_gemini(image_path):
#     """Finds menu items in an image using Google Gemini."""
#     if not genai_client:
#         return "Gemini client not initialized. Please install google-generativeai."
        
#     with open(image_path, "rb") as image_file:
#         content = image_file.read()
    
#     response = genai_client.generate_content(
#         model='gemini-pro-vision', # Using the vision model
#         contents=[
#             types.Part.from_bytes(
#                 data=content,
#                 mime_type='image/png',
#             ),
#             '''Carefully analyze the menu and find all the menu items here and return them as an array of json objects containing name (including the subtitle next to the larger title for some menu items) and price. 
#             The format returned should be similar to [{"name": "Chicken Over Rice", "price": 12.99}, {...}]. No surrounding backticks.''' 
#         ]
#     )
    
#     return response.text

def detect_with_groq(image_path):
    """Finds menu items in an image using Groq's LLaVA model."""
    try:
        groq_api_key = os.environ.get("GROQ_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_KEY environment variable not found.")
            
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        return f"Error initializing Groq client: {e}"

    # Encode the image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": '''Find all the menu items in this image and return them as an array of JSON objects containing "name" and "price".
                            The format returned should be a clean JSON array like: [{"name": "Chicken Over Rice", "price": 12.99}, {...}]. 
                            Do not include any surrounding text or markdown backticks.'''
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred while calling the Groq API: {e}"



def get_restaurant_data(img_path, name, lat, lng, city) -> RestaurantInfo:
    
    menu_items = json.loads(detect_with_groq(img_path))

    # format menu_items into MenuItem objects
    menu_items = [MenuItem(name=item['name'], category ='', price=str(item['price'])) for item in menu_items]

    

    USER_EMAIL = os.getenv("BELI_USER_EMAIL")
    USER_PASSWORD = os.getenv("BELI_USER_PASSWORD")
    USER_ID = os.getenv("USER_ID")

    beli = Beli(email=USER_EMAIL, password=USER_PASSWORD, user_id=USER_ID)

    restaurant_beli = beli.search_restaurant(name, lat, lng, city)['predictions'][0]
    google_id = restaurant_beli['place_id']

    # get maps shit
    MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    popular_items = get_popular_items_info(google_id, MAPS_API_KEY)

    beli_id = restaurant_beli['business']

    dishes = beli.get_dish_recommendations(beli_id)
    processed_dish = []
    if dishes and dishes["results"]:
        for dish in dishes["results"]:
            processed_dish.append(
                BeliTopItem(
                    name = dish["name"],
                    image = dish["photo"]["image"],
                    position = dish["rec_type"],
                )
            )

    # add beli shit at bottom 
    return RestaurantInfo(
        id=google_id,
        name=name,
        average_rating=3.5,
        review_count="",
        image_url="",
        address="",
        latitude=lat,
        longitude=lng,
        city=city,
        state="",
        price_range="",
        tags=[],
        other_info=OtherInfo(),
        menu_items=menu_items,
        reviews = popular_items,
        beli_id = str(beli_id),
        top_items = processed_dish
    )
    



# --- Main execution ---
if __name__ == "__main__":
    load_dotenv("../.env")
    image_file_path = "menu.png" # Make sure 'menu.png' is in the same directory

    get_restaurant_data(image_file_path, "Boston Shawarma", "42.341121", "-71.087783", "Boston")

    # if not os.path.exists(image_file_path):
    #     print(f"Error: Image file not found at '{image_file_path}'")
    # else:
    #     print("--- Detecting menu items with Groq ---")
    #     menu_items_groq = detect_with_groq(image_file_path)
    #     print(menu_items_groq)

        # You can uncomment the following lines to test the other functions
        # print("\n--- Detecting menu items with Gemini ---")
        # menu_items_gemini = detect_with_gemini(image_file_path)
        # print(menu_items_gemini)
        
        # print("\n--- Detecting raw text with Google Cloud Vision ---")
        # menu_text_vision = detect_text_from_image(image_file_path)
        # print(menu_text_vision)
