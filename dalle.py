import json

import requests


def generate_image_with_dalle(prompt, token):
    API_URL = "https://api.openai.com/v1/images/generations"
    HEADERS = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    PAYLOAD = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    response = requests.post(API_URL, headers=HEADERS, json=PAYLOAD)

    if response.status_code == 200:
        data = response.json()
        return data["data"][0]["url"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        raise ValueError(json.loads(response.text)["error"]["code"])
