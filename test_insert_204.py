import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import supabase

try:
    # Try inserting with returning='minimal' to see if it fixes 204
    # or see if a regular insert fails with 204.
    response = supabase.table("customers").insert({
        "name": "test_script_user",
        "email": "test_script@gmail.com",
        "company": "test"
    }).execute()
    print("Success:")
    print(response.data)
except Exception as e:
    if hasattr(e, 'json'):
        print(f"APIError: {e.json()}")
    elif hasattr(e, 'message'):
        print(f"Error message: {e.message}")
    else:
        print(f"Exact Exception: {vars(e)}")
        print(f"Exception Message: {str(e)}")
