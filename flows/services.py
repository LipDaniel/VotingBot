import os
import http.client
import json
from bs4 import BeautifulSoup
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

    conn.request("GET", "/random?type=alias", headers=headers)

    res = conn.getresponse()
    data = res.read()
    parsed_data = json.loads(data.decode("utf-8"))
    return parsed_data['email'], parsed_data['timestamp']

def get_email_mid(email, timestamp):
    conn = http.client.HTTPSConnection(base_url)

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': base_url,
        'Content-Type': "application/json"
    }
    conn.request("GET", "/inbox?email=" + email + "&timestamp=" + str(timestamp), headers=headers)
    res = conn.getresponse()
    data = res.read()
    parsed_data = json.loads(data.decode("utf-8"))
    messages = parsed_data['messages']
    if (len(messages) == 0):
        return None
    last_message = messages[len(messages) - 1]

    return last_message['mid']

def get_link_via_message(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for a in soup.find_all("a"):
        if "Xác nhận" in a.get_text():
            return a["href"]

def get_full_email_last_message(email, mid):
    conn = http.client.HTTPSConnection(base_url)

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': base_url,
        'Content-Type': "application/json"
    }
    conn.request("GET", "/message?email=" + email + "&mid=" + str(mid), headers=headers)
    res = conn.getresponse()
    data = res.read()
    parsed_data = json.loads(data.decode("utf-8"))
    get_link_via_message(parsed_data['body'])

    return parsed_data['body']
