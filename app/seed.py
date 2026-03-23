"""
Seed Script -- Meera Industries Sales Lifecycle Demo
====================================================
Populates the database with the example scenario:

  Customer:     Meera Industries
  Opportunity:  CRM Purchase

  Call 1 -> evaluating CRM tools     -> DISCOVERY   -> OPEN
  Call 2 -> integration concerns     -> EVALUATION  -> IN_PROGRESS
  Call 3 -> asks for pricing         -> NEGOTIATION -> IN_PROGRESS
  Call 4 -> agrees to purchase       -> CLOSING     -> CLOSED_WON

Run:  python -m app.seed
"""

import os
import sys

# Add parent dir to path so we can import the app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import supabase


def seed():
    print("[SEED] Seeding database with Meera Industries scenario...\n")

    # -- 1. Create Customer --
    customer = (
        supabase.table("customers")
        .insert({
            "name": "Meera Industries",
            "email": "ani@meeraindustries.com",
            "company": "Meera Industries",
            "industry": "Manufacturing",
            "company_size": "500-1000",
        })
        .execute()
    ).data[0]
    cid = customer["customer_id"]
    print(f"[OK] Customer created: {customer['name']} ({cid})")

    # -- 2. Create Opportunity --
    opportunity = (
        supabase.table("opportunities")
        .insert({
            "customer_id": cid,
            "opportunity_name": "CRM Purchase",
            "product_interest": "Enterprise CRM Suite",
            "deal_value": 75000.00,
            "stage": "LEAD",
            "status": "OPEN",
            "probability": 20.00,
            "assigned_sales_rep": "Arjun Mehta",
            "expected_close_date": "2026-04-15",
            "notes": "Meera Industries evaluating multiple CRM vendors.",
        })
        .execute()
    ).data[0]
    oid = opportunity["opportunity_id"]
    print(f"[OK] Opportunity created: {opportunity['opportunity_name']} ({oid})")

    # -- 3. Simulate 4 Calls --

    calls = [
        {
            "transcript": (
                "Hi, we are Meera Industries. We are currently evaluating CRM tools "
                "for our sales team. We have about 200 reps and need something that "
                "can handle pipeline tracking, lead scoring, and reporting. "
                "Can you tell me about your features?"
            ),
            "source": "call",
            "stage_detected": "DISCOVERY",
            "opp_stage": "DISCOVERY",
            "opp_status": "OPEN",
            "probability": 30.00,
            "sentiment": "Positive",
            "lead_score": 45.0,
            "urgency": "Low",
            "confidence": 0.82,
            "intent": "Feature exploration",
            "objection": None,
            "action": "Send product feature comparison deck",
            "email": "Hi Meera team, here is our feature comparison document...",
        },
        {
            "transcript": (
                "We liked the demo. However, we have concerns about integration with "
                "our existing ERP system. We use SAP and need bi-directional sync. "
                "Also, data migration from our current system is a worry. "
                "Not sure if this will work smoothly."
            ),
            "source": "call",
            "stage_detected": "EVALUATION",
            "opp_stage": "EVALUATION",
            "opp_status": "IN_PROGRESS",
            "probability": 50.00,
            "sentiment": "Neutral",
            "lead_score": 58.0,
            "urgency": "Medium",
            "confidence": 0.75,
            "intent": "Integration assessment",
            "objection": "uncertainty",
            "action": "Schedule technical deep-dive with integration team",
            "email": "Hi Meera team, our integration team can demo the SAP connector...",
        },
        {
            "transcript": (
                "The integration demo went well. Now we need to discuss pricing. "
                "Our budget is around $70-80K for the first year. Can we get a "
                "discount for a multi-year deal? Also, what are the implementation costs? "
                "We need a quote by next week."
            ),
            "source": "call",
            "stage_detected": "NEGOTIATION",
            "opp_stage": "NEGOTIATION",
            "opp_status": "IN_PROGRESS",
            "probability": 70.00,
            "sentiment": "Positive",
            "lead_score": 78.0,
            "urgency": "High",
            "confidence": 0.88,
            "intent": "Pricing negotiation",
            "objection": "price_concern",
            "action": "Prepare custom pricing proposal with multi-year discount",
            "email": "Hi Meera team, attached is our custom pricing proposal...",
        },
        {
            "transcript": (
                "We have reviewed the proposal internally and our management has "
                "approved the purchase. We want to go ahead with the 3-year plan. "
                "Please send us the contract. We'd like to start implementation "
                "by next month."
            ),
            "source": "call",
            "stage_detected": "CLOSING",
            "opp_stage": "CLOSING",
            "opp_status": "CLOSED_WON",
            "probability": 100.00,
            "sentiment": "Positive",
            "lead_score": 95.0,
            "urgency": "High",
            "confidence": 0.96,
            "intent": "Purchase confirmation",
            "objection": None,
            "action": "Send formal contract and initiate onboarding",
            "email": "Congratulations! We are excited to welcome Meera Industries...",
        },
    ]

    for i, call in enumerate(calls, 1):
        print(f"\n[CALL {i}] {call['intent']}")

        # Insert conversation
        conv = (
            supabase.table("conversations")
            .insert({
                "opportunity_id": oid,
                "customer_id": cid,
                "transcript": call["transcript"],
                "source": call["source"],
            })
            .execute()
        ).data[0]
        conv_id = conv["conversation_id"]
        print(f"   [CONV] Conversation recorded ({conv_id[:8]}...)")

        # Insert AI insight
        insight_data = {
            "conversation_id": conv_id,
            "intent": call["intent"],
            "sentiment": call["sentiment"],
            "lead_score": call["lead_score"],
            "stage_detected": call["stage_detected"],
            "urgency": call["urgency"],
            "confidence": call["confidence"],
        }
        if call["objection"]:
            insight_data["objection"] = call["objection"]

        supabase.table("ai_insights").insert(insight_data).execute()
        print(f"   [AI]   stage={call['stage_detected']}, "
              f"sentiment={call['sentiment']}, lead_score={call['lead_score']}")

        # Insert action
        supabase.table("actions").insert({
            "conversation_id": conv_id,
            "next_best_action": call["action"],
            "email_generated": call["email"],
            "task_created": call["action"],
            "assigned_to": "Arjun Mehta",
            "status": "COMPLETED" if i < 4 else "PENDING",
        }).execute()
        print(f"   [ACT]  {call['action']}")

        # Update opportunity stage and status
        supabase.table("opportunities").update({
            "stage": call["opp_stage"],
            "status": call["opp_status"],
            "probability": call["probability"],
        }).eq("opportunity_id", oid).execute()
        print(f"   [OPP]  stage={call['opp_stage']}, status={call['opp_status']}")

    print("\n" + "=" * 60)
    print("[DONE] Seed complete! The Meera Industries lifecycle is ready.")
    print(f"   Customer ID:    {cid}")
    print(f"   Opportunity ID: {oid}")
    print("=" * 60)


if __name__ == "__main__":
    seed()
