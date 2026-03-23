import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found!")
    exit(1)

print(f"✓ API Key loaded (starts with: {api_key[:20]}...)")

# Gemini API endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

# Prepare the request
payload = {
    "contents": [
        {
            "parts": [
                {"text": "Say hello and return status ok"}
            ]
        }
    ]
}

print("\n" + "="*50)
print("Sending request to Google Gemini API...")
print("="*50)

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Success!")
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"✗ Error!")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection Error: {e}")
    print("\nPossible causes:")
    print("  1. No internet connection")
    print("  2. Firewall blocking Google API")
    print("  3. Proxy configuration needed")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
