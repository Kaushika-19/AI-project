from app.recommendation import next_best_action
import json

analysis_data = {
  "conversation_summary": "The customer inquired about pricing and was quoted $100, but immediately raised a concern regarding integration.",
  "interest": {
    "interest_score_0_100": 60,
    "signals": ["Inquired about pricing"]
  },
  "sentiment": {"sentiment": "Neutral", "sentiment_compound": 0.0},
  "objections": {"objections": ["Not sure about integration"], "objection_count": 1},
  "buying_stage": {"buying_stage": "EVALUATION"},
  "urgency": {"urgency_level": "Low"},
  "conversion_score_0_100": 45.0
}

try:
    result = next_best_action(analysis_data)
    print("Recommendation Result:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print("Error during recommendation:", e)
