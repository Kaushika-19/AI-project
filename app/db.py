"""
Supabase Database Client
========================
Initializes the Supabase client for all database operations.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment. "
        "Add them to your .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
