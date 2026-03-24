import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import supabase, SUPABASE_URL, SUPABASE_KEY

print(f"URL: {SUPABASE_URL is not None}")
print(f"KEY: {SUPABASE_KEY is not None}")

try:
    response = supabase.table("customers").select("count").limit(1).execute()
    print("Successfully connected to Supabase!")
    print(response.data)
except Exception as e:
    print(f"Failed to connect to Supabase: {e}")
