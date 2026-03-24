import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.recommendation import next_best_action

print(next_best_action({
    "conversation_summary": "Test summary",
    "interest": "High",
    "Customer": "Test Client"
}))
