import os
import json
from dotenv import load_dotenv
from app.recommendation import next_best_action

load_dotenv()

test_data = {
    "conversation_summary": "Customer is interested in CRM with WhatsApp integration. High urgency.",
    "interest": {"interest_score_0_100": 85, "signals": {}},
    "trust": {"trust_score_0_100": 70, "signals": {}},
    "sentiment": {"sentiment": "Positive", "sentiment_compound": 0.5},
    "objections": {"objections": ["pricing"], "objection_count": 1},
    "buying_stage": {"buying_stage": "Evaluation", "stage_scores": {}},
    "urgency": {"urgency_level": "High", "urgency_hits": 2},
    "conversion_score_0_100": 80.0
}

print("Testing next_best_action...")
result = next_best_action(test_data)
print(json.dumps(result, indent=2))
