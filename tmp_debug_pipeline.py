import sys
import os
import asyncio
from datetime import datetime

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.pipeline import analyze_text
from app.db import engine
from sqlalchemy import text

async def test_analyze():
    print("--- Starting Backend Test ---")
    
    # Check DB connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Database connection: OK")
    except Exception as e:
        print(f"Database connection: FAILED - {e}")
        return

    # Try a simple text analysis
    try:
        print("Testing analyze_text...")
        # Note: This requires a valid opportunity_id in the DB. 
        # I'll try to find one first.
        with engine.connect() as conn:
            result = conn.execute(text("SELECT opportunity_id FROM opportunities LIMIT 1")).fetchone()
            if result:
                opp_id = result[0]
                print(f"Using opportunity_id: {opp_id}")
                
                analysis = await analyze_text(
                    opportunity_id=opp_id,
                    transcript="Client is very interested in the premium plan but needs a 10% discount. Let's follow up next Monday.",
                    email=None
                )
                print("Analysis Result: SUCCESS")
                print(f"Conversation ID: {analysis.get('conversation_id')}")
                print(f"Suggestions Count: {len(analysis.get('suggestions', []))}")
            else:
                print("No opportunities found in DB to test with.")
    except Exception as e:
        print(f"Analysis: FAILED")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_analyze())
