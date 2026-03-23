import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")

print("Initializing client...")
client = genai.Client(api_key=api_key)

try:
    print("Sending request to gemini-pro-latest...")
    response = client.models.generate_content(
        model="models/gemini-flash-lite-latest",
        contents="Say hello and return a JSON {'status': 'ok'}",
        config=GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    print("Response received!")
    print("Response text:", response.text)
except Exception as e:
    print("Caught exception:", e)
print("Script finished.")
