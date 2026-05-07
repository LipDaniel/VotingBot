import os
import http.client
from dotenv import load_dotenv
load_dotenv()

base_url = os.getenv("RAPID_BASE_URL")
api_key = os.getenv("RAPID_API_KEY")

def get_temp_email():
    conn = http.client.HTTPSConnection(base_url)

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': base_url,
        'Content-Type': "application/json"
    }

    conn.request("GET", "/random?type=alias&password=abc123", headers=headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))
    return data