from app.scoring import analyze_call
import json

transcript = "Customer: I am interested in the pricing. Sales: It is 100 dollars. Customer: I am not sure about integration."
try:
    result = analyze_call(transcript)
    print("Analysis Result:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print("Error during analysis:", e)
