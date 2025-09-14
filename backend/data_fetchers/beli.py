import requests
import json


class Beli:
    """
    A client to interact with the restaurant API, with built-in
    logic to automatically refresh expired authentication tokens.
    """

    def __init__(self, email, password, user_id):
        self.base_url = "https://backoffice-service-t57o3dxfca-nn.a.run.app/api/"
        self.email = email
        self.password = password
        self.user_id = user_id
        self.access_token = None  # Will be populated on the first call or refresh

    def _refresh_token(self):
        """
        Refreshes the access token using the stored credentials.
        """
        token_url = f"{self.base_url}token/"
        print("\n--- Token expired or missing. Refreshing token... ---")

        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "origin": "capacitor://localhost",
        }

        data = {"password": self.password, "email": self.email}

        try:
            response = requests.post(token_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access")

            if self.access_token:
                print("--- Successfully refreshed token. ---")
                return True
            else:
                print("--- Failed to refresh token: 'access' key not in response. ---")
                return False
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during token refresh: {e}")
            return False

    def _make_request(self, method, endpoint, params=None):
        """
        A centralized method to make API requests, handling token refresh and retries.
        """
        if not self.access_token:
            if not self._refresh_token():
                print("Could not get initial token. Aborting request.")
                return None

        url = f"{self.base_url}{endpoint}"

        headers = {
            "accept": "application/json",
            "origin": "capacitor://localhost",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "authorization": f"Bearer {self.access_token}",
        }

        try:
            response = requests.request(method, url, headers=headers, params=params)

            if response.status_code == 401:
                print("Authorization error (401). Retrying with a new token...")
                if self._refresh_token():
                    headers["authorization"] = f"Bearer {self.access_token}"
                    print("Retrying the request...")
                    response = requests.request(
                        method, url, headers=headers, params=params
                    )

            response.raise_for_status()
            print(f"Request to '{endpoint}' successful!")
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred for {endpoint}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred with the request to {endpoint}: {req_err}")

        return None

    def search_restaurant(self, name, lat, lng, city):
        """
        Searches for a restaurant using its name and location.
        """
        params = {
            "coords": f"{lat},{lng}",
            "term": name,
            "user": self.user_id,
            "city": city,
        }
        return self._make_request("GET", "search-app/", params=params)

    def get_dish_recommendations(self, business_id, version="7.9.4", menu_vibes=True):
        """
        Gets dish recommendations for a specific restaurant.

        Args:
            business_id (str or int): The unique ID of the business.
            version (str): The client version string.
            menu_vibes (bool): Flag to include menu vibes.
        """
        params = {
            "business": business_id,
            "version": version,
            "menu_vibes": str(
                menu_vibes
            ).lower(),  # Convert boolean to 'true'/'false' string
        }
        return self._make_request("GET", "dish-rec/", params=params)

    def get_complete_res_info(self, name, lat, lng, city):
        res = self.search_restaurant(name, lat, lng, city)
        if res:
            if res["predictions"]:
                print(res["predictions"][0]["place_id"])
                business_id = res["predictions"][0]["business"]
                dishes = self.get_dish_recommendations(business_id)
                processed_dish = []
                if dishes and dishes["results"]:
                    for dish in dishes["results"]:
                        processed_dish.append(
                            {
                                "name": dish["name"],
                                "image": dish["photo"]["image"],
                                "position": dish["rec_type"],
                            }
                        )
                return True, business_id, processed_dish
        return False, "", []
