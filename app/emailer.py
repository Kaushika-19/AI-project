import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RESEND_API_KEY")
URL = "https://api.resend.com/emails"


def send_email(to_email: str, subject: str, html: str):

    data = {
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": subject,
        "html": html
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, json=data, headers=headers)

    return response.json()