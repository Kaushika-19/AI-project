import os
import json
import sys
from dotenv import load_dotenv

print("=" * 50)
print("Step 1: Load environment")
print("=" * 50)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key starts with: {api_key[:20]}...")

print("\n" + "=" * 50)
print("Step 2: Initialize Gemini client")
print("=" * 50)
try:
    from google import genai
    from google.genai.types import GenerateContentConfig
    print("✓ Imported genai libraries")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)
    print("✓ Client initialized")
except Exception as e:
    print(f"✗ Failed to initialize client: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("Step 3: List available models")
print("=" * 50)
try:
    models = client.models.list()
    print("Available models:")
    for model in models:
        print(f"  - {model.name}")
except Exception as e:
    print(f"✗ Failed to list models: {e}")

print("\n" + "=" * 50)
print("Step 4: Send simple request (NO JSON mode)")
print("=" * 50)
try:
    print("Sending request...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say 'Hello from Gemini!' and nothing else.",
    )
    print("✓ Response received!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("Step 5: Send JSON request")
print("=" * 50)
try:
    print("Sending JSON request...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Return only valid JSON: {'status': 'ok', 'message': 'success'}",
        config=GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    print("✓ Response received!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")

print("\nDebug complete!")
