import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import supabase

try:
    response = supabase.table("customers").insert({
        "name": "test_script_user",
        "email": "test_script@gmail.com",
        "company": "test"
    }).execute()
    print("Success:")
    print(response)
except Exception as e:
    print(f"Exception Type: {type(e)}")
    print(f"Exception Message: {e}")
