# import os
# import json
# import sys
# from datetime import datetime
# from dotenv import load_dotenv
# from google import genai
# from google.genai.types import GenerateContentConfig

# # ---------------------------------
# # Load Environment Variables
# # ---------------------------------
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")

# if not api_key:
#     raise ValueError("GEMINI_API_KEY not found in .env file")

# client = genai.Client(api_key=api_key)


# # ---------------------------------
# # Safe JSON Repair Function
# # ---------------------------------
# def repair_json(raw_text):
#     """
#     Attempts to repair truncated JSON.
#     """
#     try:
#         return json.loads(raw_text)
#     except:
#         # Try to close braces if truncated
#         if not raw_text.strip().endswith("}"):
#             raw_text = raw_text + '"}\n}'
#         try:
#             return json.loads(raw_text)
#         except:
#             return None


# # ---------------------------------
# # Core Decision Engine
# # ---------------------------------
# def decision_engine_from_file(json_file_path: str):

#     # ---- Step 1: Read JSON file ----
#     try:
#         with open(json_file_path, "r", encoding="utf-8") as file:
#             input_data = json.load(file)
#     except Exception as e:
#         return {"error": f"Failed to read JSON file: {str(e)}"}

#     today = datetime.today().strftime("%Y-%m-%d")

#     # ---- Step 2: Prompt ----
#     prompt = f"""
# You are an AI Sales Decision Engine.

# Analyze the CRM intelligence JSON provided.

# Return STRICT JSON with:

# - next_best_action
# - confidence_level_0_to_1
# - risk_level (Low/Medium/High)
# - next_reminder_date (YYYY-MM-DD)
# - email_draft (keep under 120 words)
# - reasoning (brief)

# Do NOT exceed 600 words total.
# Do NOT cut JSON.
# Return only JSON.

# Today's date: {today}

# Input JSON:
# {json.dumps(input_data, indent=2)}
# """

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt,
#             config=GenerateContentConfig(
#                 temperature=0.2,
#                 max_output_tokens=4096,   # 🔥 increased
#                 response_mime_type="application/json"
#             ),
#         )

#         raw_output = response.text.strip()

#         parsed = repair_json(raw_output)

#         if parsed:
#             return parsed
#         else:
#             return {
#                 "error": "Model returned incomplete JSON",
#                 "raw_output": raw_output
#             }

#     except Exception as e:
#         return {"error": f"Prediction failed: {str(e)}"}


# # ---------------------------------
# # Run From Terminal
# # ---------------------------------
# if __name__ == "__main__":

#     if len(sys.argv) != 2:
#         print("Usage: python app.py your_file.json")
#         sys.exit(1)

#     result = decision_engine_from_file(sys.argv[1])
#     print(json.dumps(result, indent=2))


# deal_data.json


# {
#   "conversation_summary": "Customer is exploring a CRM and asks about WhatsApp integration and onboarding. They plan rollout next month, have pricing concerns, want a quote and demo this week, but need manager approval.",
#   "interest": {
#     "interest_score_0_100": 69.25,
#     "signals": {
#       "curiosity_0_1": 0.5,
#       "future_planning_0_1": 1.0,
#       "positive_language_0_1": 0.55,
#       "engagement_depth_0_1": 0.7
#     }
#   },
#   "trust": {
#     "trust_score_0_100": 68.25,
#     "signals": {
#       "tone_consistency_0_1": 0.75,
#       "openness_0_1": 0.67,
#       "responsiveness_0_1": 0.8,
#       "confidence_0_1": 0.45
#     }
#   },
#   "sentiment": {
#     "sentiment": "Neutral",
#     "sentiment_compound_-1_to_1": 0.1
#   },
#   "objections": {
#     "objections": [
#       "price_concern",
#       "uncertainty"
#     ],
#     "objection_details": {
#       "price_concern": {
#         "count": 1
#       },
#       "uncertainty": {
#         "count": 2
#       }
#     },
#     "objection_count": 3
#   },
#   "buying_stage": {
#     "buying_stage": "Negotiation",
#     "stage_scores": {
#       "Awareness": 1,
#       "Interest": 0,
#       "Evaluation": 2,
#       "Negotiation": 3,
#       "Decision": 1
#     }
#   },
#   "urgency": {
#     "urgency_level": "High",
#     "urgency_hits": 1,
#     "action_commitment": true
#   },
#   "conversion_score_0_100": 70.0
# }







import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class SuggestionSchema(BaseModel):
    title: str = Field(description="Short name of the action")
    next_best_action: str = Field(description="Detailed description of the action")
    confidence_level_0_to_1: float = Field(description="Confidence score")
    risk_level: str = Field(description="Low, Medium, or High")
    next_reminder_date: str = Field(description="YYYY-MM-DD format")
    reasoning: str = Field(description="Brief explanation of why this action is recommended")
    email_draft: str = Field(
        description=(
            "A fully written, ready-to-send email for this specific action, "
            "including greeting with customer name (if provided), clear body, "
            "CTA and sign-off. 120–200 words."
        )
    )

class RecommendationSchema(BaseModel):
    suggestions: List[SuggestionSchema] = Field(description="List of 3 distinct strategic recommendations with specific email drafts")

# -----------------------------
# NEXT BEST ACTION ENGINE
# -----------------------------
def next_best_action(analysis_data: dict):

    today = datetime.today().strftime("%Y-%m-%d")

    parser = PydanticOutputParser(pydantic_object=RecommendationSchema)

    prompt = PromptTemplate(
        template=(
            "You are an AI Sales Decision Engine.\n"
            "{format_instructions}\n\n"
            "You receive rich CRM intelligence plus context.\n"
            "Fields may include:\n"
            "- conversation_summary, interest, trust, objections, buying_stage, urgency\n"
            "- customer_name, customer_company, customer_email\n"
            "- opportunity_name, opportunity_stage, opportunity_status, deal_value, expected_close_date\n\n"
            "TASK:\n"
            "1) Suggest the TOP 3 distinct, high-quality strategic options for the sales rep.\n"
            "2) For each suggestion, generate a COMPLETE email in 'email_draft' that is ready to send:\n"
            "   - Start with: \"Hi <customer_name>,\" or \"Hi there,\" if name missing.\n"
            "   - Reference the specific opportunity / product and conversation_summary.\n"
            "   - Address key objections and urgency explicitly.\n"
            "   - Include a clear call-to-action with a proposed next step and timing.\n"
            "   - Close with a professional sign-off (e.g., \"Best regards,\" plus a generic rep signature).\n"
            "   - Length around 120–200 words.\n\n"
            "Today's Date: {today}\n"
            "Input Data: {data}\n"
        ),
        input_variables=["today", "data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        
        chain = prompt | model | parser
        result = chain.invoke({"today": today, "data": json.dumps(analysis_data)})
        print("lang working")
        return result.model_dump()

    except Exception as e:
        print(f"LangChain Recommendation Error: {e}")
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