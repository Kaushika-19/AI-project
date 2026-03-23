"""
Supabase Database Client
========================
Initializes the Supabase client for all database operations.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = "https://snodirqiucxpcsdculmf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNub2RpcnFpdWN4cGNzZGN1bG1mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3OTQzMjYsImV4cCI6MjA4ODM3MDMyNn0.X1d-dN_QbKVNP-X4rqVvNoD6jA2dbUjJPvNasOAMCKI"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment. "
        "Add them to your .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
