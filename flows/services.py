from email.message import EmailMessage
import os
import http.client
import json
import smtplib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

SMTP_EMAIL = "nhan.nguyenkieu317@gmail.com"
SMTP_PASSWORD = "turj zesd uttt laka"
FORWARD_TO = "nhan.nguyenkieu317@gmail.com"

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

def get_email_subject(parsed_data):
    return (
        parsed_data.get("subject")
        or parsed_data.get("title")
        or parsed_data.get("mail_subject")
        or parsed_data.get("headers", {}).get("subject")
        or "Xác nhận tài khoản đăng ký"
    )


def get_email_from(parsed_data):
    return (
        parsed_data.get("from")
        or parsed_data.get("sender")
        or parsed_data.get("mail_from")
        or parsed_data.get("headers", {}).get("from")
        or SMTP_EMAIL
    )

def forward_email(subject, sender, body):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = FORWARD_TO

    if sender:
        msg["Reply-To"] = "ELLE Viet Nam"

    msg.set_content("This email contains HTML content.")
    msg.add_alternative(body, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)

    print(">>> EMAIL FORWARDED!")

def get_full_email_last_message(email, mid):
    conn = http.client.HTTPSConnection(base_url)

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': base_url,
        'Content-Type': "application/json"
    }

    conn.request(
        "GET",
        "/message?email=" + email + "&mid=" + str(mid),
        headers=headers
    )

    res = conn.getresponse()
    data = res.read()

    parsed_data = json.loads(data.decode("utf-8"))

    body = parsed_data['body']

    get_link_via_message(body)

    # Forward mail
    subject = get_email_subject(parsed_data)
    sender = get_email_from(parsed_data)
    
    forward_email(subject, sender, body)

    return body
