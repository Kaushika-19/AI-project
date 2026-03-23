from .speech import transcribe_call
from .scoring import analyze_call
from .emailer import send_email
from .recommendation import next_best_action
from . import crud
from .models import ConversationCreate, AIInsightCreate, ActionCreate, OpportunityUpdate, ConversationSource
from datetime import datetime, timedelta

def build_transcript(utterances):
    return " ".join([u["text"] for u in utterances])

def map_speakers(utterances):
    turns = []
    for u in utterances:
        role = "customer" if u["speaker"] == 1 else "agent"
        turns.append((role, u["text"]))
    return turns

def generate_email(result, action_item, deadline):
    stage = result["buying_stage"]["buying_stage"]
    urgency = result["urgency"]["urgency_level"]
    summary = result["conversation_summary"]
    
    deadline_str = deadline.strftime("%A, %b %d")

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; line-height: 1.6; color: #333;">
        <h2 style="color: #2563eb;">Meeting Follow-up & Next Steps</h2>
        <p>Thank you for the productive discussion today.</p>
        
        <div style="background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
            <p><b>Conversation Summary:</b><br/>{summary}</p>
        </div>

        <p>Based on our talk, we've identified the following <b>Next Best Action</b>:</p>
        <div style="background: #eff6ff; padding: 15px; border-radius: 8px; border: 1px solid #bfdbfe;">
            <p style="margin: 0; font-size: 1.1rem; color: #1e40af;"><b>{action_item}</b></p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #64748b;">Target Completion: <b>{deadline_str}</b></p>
        </div>

        <p>Our records show we are currently in the <b>{stage}</b> stage with <b>{urgency}</b> priority. We are committed to moving this forward quickly.</p>
        
        <p>Best regards,<br/>Sales Intelligence Team</p>
    </div>
    """

def analyze_audio(file_path: str, opportunity_id: str, email: str | None = None):
    # 1. Transcribe
    utterances = transcribe_call(file_path)
    transcript = build_transcript(utterances)
    speaker_turns = map_speakers(utterances)
    return process_pipeline(transcript, opportunity_id, "call", speaker_turns, email)

def analyze_text(transcript: str, opportunity_id: str, email: str | None = None):
    return process_pipeline(transcript, opportunity_id, "chat", None, email)

def process_pipeline(transcript: str, opportunity_id: str, source: str, speaker_turns: list | None, email: str | None):
    # 1. Get Opportunity info
    try:
        opp = crud.get_opportunity(opportunity_id)
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        # Also fetch customer so we can personalize emails
        customer = crud.get_customer(opp["customer_id"])
    except Exception as e:
        print(f"Error fetching opportunity: {e}")
        raise ValueError(f"CRITICAL: Failed to retrieve opportunity {opportunity_id}")

    # 2. Save Conversation
    try:
        conv_in = ConversationCreate(
            opportunity_id=opportunity_id,
            customer_id=opp["customer_id"],
            transcript=transcript,
            source=source
        )
        conv = crud.create_conversation(conv_in)
        conv_id = conv["conversation_id"]
    except Exception as e:
        print(f"Error saving conversation: {e}")
        # Return fallback if conversation cannot be saved (though this is serious)
        conv_id = "failed_to_save"

    # 3. AI Analysis (Local Scoring)
    try:
        result = analyze_call(transcript, speaker_turns)
    except Exception as e:
        print(f"Error in analyze_call locally: {e}")
        result = {
            "conversation_summary": "Failed to generate summary.",
            "interest": {"interest_score_0_100": 50, "signals": {}},
            "trust": {"trust_score_0_100": 50, "signals": {}},
            "sentiment": {"sentiment": "Neutral", "sentiment_compound": 0.0},
            "objections": {"objections": [], "objection_count": 0},
            "buying_stage": {"buying_stage": "Unknown", "stage_scores": {}},
            "urgency": {"urgency_level": "Medium", "urgency_hits": 0},
            "conversion_score_0_100": 50.0
        }
    
    # 4. Save AI Insights
    if conv_id != "failed_to_save":
        try:
            # Handle objections: join list into string or set to None
            objections_list = result["objections"].get("objections", [])
            objection_text = ", ".join([str(o) for o in objections_list]) if objections_list else None

            insight_in = AIInsightCreate(
                conversation_id=conv_id,
                intent=result.get("conversation_summary", ""), 
                sentiment=result["sentiment"].get("sentiment", "Neutral"),
                lead_score=result.get("conversion_score_0_100", 0.0),
                objection=objection_text,
                stage_detected=result["buying_stage"].get("buying_stage", "DISCOVERY").upper(),
                urgency=result["urgency"].get("urgency_level", "Medium")
            )
            crud.create_ai_insight(insight_in)
        except Exception as e:
            print(f"Error saving AI insights: {e}")

    # 5. Suggestions (Gemini Engine)
    try:
        # Enrich analysis with CRM context for better, personalized emails
        enriched = dict(result)
        try:
            if opp:
                enriched["opportunity_name"] = opp.get("opportunity_name")
                enriched["opportunity_stage"] = opp.get("stage")
                enriched["opportunity_status"] = opp.get("status")
                enriched["deal_value"] = opp.get("deal_value")
                enriched["expected_close_date"] = str(opp.get("expected_close_date")) if opp.get("expected_close_date") else None
            if customer:
                enriched["customer_name"] = customer.get("name")
                enriched["customer_company"] = customer.get("company")
                enriched["customer_email"] = customer.get("email")
        except Exception as ctx_err:
            print(f"Error enriching analysis context: {ctx_err}")

        decision = next_best_action(enriched)
        suggestions = decision.get("suggestions", [])
    except Exception as e:
        print(f"Error in next_best_action: {e}")
        suggestions = []
    
    # We no longer auto-save an action here, as the salesperson 
    # will now choose one of the 3 suggestions or enter a custom 
    # one in the frontend.
    
    top_suggestion = suggestions[0] if suggestions else {
        "next_best_action": "Follow up with customer",
        "next_reminder_date": (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")
    }
    action_desc = top_suggestion.get("next_best_action", "Follow up with customer")
    deadline = datetime.utcnow() + timedelta(days=2) # Default for email preview only
    
    if suggestions:
        try:
            deadline = datetime.strptime(suggestions[0]["next_reminder_date"], "%Y-%m-%d")
        except:
            pass

    # 6. Update Opportunity Stage
    try:
        new_stage = result["buying_stage"].get("buying_stage", "DISCOVERY").upper()
        if new_stage and new_stage != "UNKNOWN":
            opp_update = OpportunityUpdate(stage=new_stage)
            
            if result.get("conversion_score_0_100", 0) > 80:
                current_prob = opp.get("probability", 0) or 0
                opp_update.probability = min(100, current_prob + 15)
            
            crud.update_opportunity(opportunity_id, opp_update)
    except Exception as e:
        print(f"Error updating opportunity: {e}")

    # 7. Prepare Email Preview (Fallback)
    email_html = "Email template will be generated based on your chosen decision."
    # Email sending moved to action confirmation for better accuracy

    return {
        "conversation_id": conv_id,
        "transcript": transcript,
        "analysis": result,
        "email_preview": email_html,
        "action_suggested": action_desc,
        "deadline": deadline.isoformat(),
        "suggestions": suggestions
    }

