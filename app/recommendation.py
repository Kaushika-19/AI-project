import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv(override=True)
api_key = os.getenv("API_KEY")

# -----------------------------
# NEXT BEST ACTION ENGINE
# -----------------------------
def next_best_action(analysis_data: dict):

    today = datetime.today().strftime("%Y-%m-%d")

    prompt = f"""You are an AI Sales Decision Engine.

You receive rich CRM intelligence plus context.
Fields may include:
- conversation_summary, interest, trust, objections, buying_stage, urgency
- customer_name, customer_company, customer_email
- opportunity_name, opportunity_stage, opportunity_status, deal_value, expected_close_date

TASK:
1) Suggest the TOP 3 distinct, high-quality strategic options for the sales rep.
2) For each suggestion, generate a COMPLETE email in 'email_draft' that is ready to send:
   - Start with: "Hi <customer_name>," or "Hi there," if name missing.
   - Reference the specific opportunity / product and conversation_summary.
   - Address key objections and urgency explicitly.
   - Include a clear call-to-action with a proposed next step and timing.
   - Close with a professional sign-off (e.g., "Best regards," plus a generic rep signature).
   - Length around 120-200 words.

Today's Date: {today}
Input Data: {json.dumps(analysis_data, indent=2)}

RETURN ONLY JSON matching this EXACT structure (do not include markdown codeblocks or other text):
{{
  "suggestions": [
    {{
      "title": "Short name of the action",
      "next_best_action": "Detailed description of the action",
      "confidence_level_0_to_1": 0.9,
      "risk_level": "Low",
      "next_reminder_date": "YYYY-MM-DD",
      "reasoning": "Brief explanation of why this action is recommended",
      "email_draft": "Your email here"
    }}
  ]
}}
"""

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-2.5-flash",
            "max_tokens": 1500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        resp_json = response.json()
        content = resp_json["choices"][0]["message"]["content"].strip()
        
        # Strip markdown formatting if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
            
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        return json.loads(content)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"OpenRouter Recommendation Error: {e}")
        
        # Print actual response content for debugging if available
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response Body: {response.text}")

        return {
            "suggestions": [
                {
                    "title": "Manual Follow up",
                    "next_best_action": "Reach out to the customer to confirm next steps and schedule a detailed discussion.",
                    "confidence_level_0_to_1": 0.5,
                    "risk_level": "Low",
                    "next_reminder_date": today,
                    "reasoning": "Service interruption fallback",
                    "email_draft": "Hi, I'm following up on our recent conversation to see if you have any further questions..."
                },
                {
                    "title": "Email Discovery",
                    "next_best_action": "Send a discovery email asking about current pain points and integrations.",
                    "confidence_level_0_to_1": 0.4,
                    "risk_level": "Low",
                    "next_reminder_date": today,
                    "reasoning": "Fallthrough discovery option.",
                    "email_draft": "Hi, I'd love to learn more about your current processes and how we can help..."
                },
                {
                    "title": "Demo Offer",
                    "next_best_action": "Offer a personalized product demo focusing on core features.",
                    "confidence_level_0_to_1": 0.4,
                    "risk_level": "Medium",
                    "next_reminder_date": today,
                    "reasoning": "Engagement option.",
                    "email_draft": "Hi, I'd like to offer you a personalized demo of our platform..."
                }
            ]
        }