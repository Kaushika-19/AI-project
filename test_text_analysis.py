import os
import json
from dotenv import load_dotenv
from app.pipeline import analyze_text

load_dotenv()

# Sample transcript
transcript = """
Sales: Hello, this is John from NeoVerse.
Customer: Hi John, I'm interested in your platform for our 50-person sales team.
Sales: Great! What specific features are you looking for?
Customer: We need AI-driven insights and a clear way to see our top next actions.
Sales: We have exactly that. Our AI analyzes calls and suggests strategic options.
Customer: Does it integrate with our CRM?
Sales: Yes, we have standard integrations for most major CRMs.
Customer: Okay, can you send me some pricing information?
Sales: Certainly. I'll send over a customized proposal today.
"""

opportunity_id = "test-opp-id"

# Mocking the crud call if needed, but the actual pipeline will fail if it can't find the opp in Supabase
# So let's use a real or at least existing opp id if we have one.

# Let's see what opps are in DB
from app.db import supabase
try:
    opps = supabase.table("opportunities").select("*").limit(1).execute()
    if opps.data:
        opp_id = opps.data[0]["opportunity_id"]
        print(f"Testing with dummy ID or real ID: {opp_id}")
        result = analyze_text(transcript, opp_id)
        print("Analysis Successful!")
        print(json.dumps(result, indent=2))
    else:
        print("No opportunities found to test with.")
except Exception as e:
    print(f"Test failed: {e}")
