"""
API Routes for Sales Conversation Intelligence
===============================================
RESTful endpoints for managing customers, opportunities,
conversations, AI insights, and actions.
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Body
from typing import Optional, List
import shutil
import os
from datetime import datetime, timezone
import threading
import time

from . import crud
from .models import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    OpportunityCreate, OpportunityUpdate, OpportunityResponse,
    ConversationCreate, ConversationResponse,
    AIInsightCreate, AIInsightResponse,
    ActionCreate, ActionUpdate, ActionResponse,
    OpportunityStatus, SalesStage,
    AnalysisResponse
)
from .pipeline import analyze_audio, analyze_text

router = APIRouter(prefix="/api/v1", tags=["Sales Intelligence"])


# =============================================
# CUSTOMER ENDPOINTS
# =============================================

@router.post("/customers", response_model=dict, status_code=201)
def create_customer(payload: CustomerCreate):
    """Create a new customer."""
    try:
        return crud.create_customer(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers", response_model=List[dict])
def list_customers(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List all customers with pagination."""
    return crud.list_customers(limit=limit, offset=offset)


@router.get("/customers/{customer_id}", response_model=dict)
def get_customer(customer_id: str):
    """Retrieve a customer by ID."""
    result = crud.get_customer(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


@router.put("/customers/{customer_id}", response_model=dict)
def update_customer(customer_id: str, payload: CustomerUpdate):
    """Update customer details."""
    try:
        return crud.update_customer(customer_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: str):
    """Delete a customer and all related records."""
    crud.delete_customer(customer_id)


@router.get("/customers/{customer_id}/history", response_model=dict)
def get_customer_history(customer_id: str):
    """
    Retrieve the complete history for a customer:
    all opportunities → conversations → AI insights → actions.
    """
    result = crud.get_customer_history(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


# =============================================
# OPPORTUNITY ENDPOINTS
# =============================================

@router.post("/opportunities", response_model=dict, status_code=201)
def create_opportunity(payload: OpportunityCreate):
    """Create a new sales opportunity."""
    try:
        return crud.create_opportunity(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/opportunities", response_model=List[dict])
def list_opportunities(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    stage: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List opportunities with optional filters."""
    return crud.list_opportunities(
        customer_id=customer_id,
        status=status,
        stage=stage,
        limit=limit,
        offset=offset,
    )


@router.get("/opportunities/{opportunity_id}", response_model=dict)
def get_opportunity(opportunity_id: str):
    """Retrieve a single opportunity."""
    result = crud.get_opportunity(opportunity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return result


@router.put("/opportunities/{opportunity_id}", response_model=dict)
def update_opportunity(opportunity_id: str, payload: OpportunityUpdate):
    """
    Update an opportunity — stage, status, deal value, etc.
    The database automatically sets:
      - last_updated to now()
      - closed_date when status → CLOSED_WON or CLOSED_LOST
    """
    try:
        return crud.update_opportunity(opportunity_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/opportunities/{opportunity_id}", status_code=204)
def delete_opportunity(opportunity_id: str):
    """Delete an opportunity."""
    crud.delete_opportunity(opportunity_id)


@router.get("/opportunities/{opportunity_id}/timeline", response_model=dict)
def get_opportunity_timeline(opportunity_id: str):
    """
    Get the full conversation timeline for an opportunity,
    showing deal progression through stages.
    """
    result = crud.get_opportunity_timeline(opportunity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return result


# =============================================
# CONVERSATION ENDPOINTS
# =============================================

@router.post("/conversations", response_model=dict, status_code=201)
def create_conversation(payload: ConversationCreate):
    """Record a new conversation."""
    try:
        return crud.create_conversation(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conversations", response_model=List[dict])
def list_conversations(
    opportunity_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List conversations with optional filters."""
    return crud.list_conversations(
        opportunity_id=opportunity_id,
        customer_id=customer_id,
        source=source,
        limit=limit,
        offset=offset,
    )


@router.get("/conversations/{conversation_id}", response_model=dict)
def get_conversation(conversation_id: str):
    """Retrieve a single conversation."""
    result = crud.get_conversation(conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str):
    """Delete a conversation (cascades to insights and actions)."""
    crud.delete_conversation(conversation_id)


# =============================================
# AI INSIGHT ENDPOINTS
# =============================================

@router.post("/insights", response_model=dict, status_code=201)
def create_ai_insight(payload: AIInsightCreate):
    """Store AI-generated insights for a conversation."""
    try:
        return crud.create_ai_insight(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/{conversation_id}", response_model=dict)
def get_ai_insight(conversation_id: str):
    """Retrieve the AI insight for a specific conversation."""
    result = crud.get_ai_insight_by_conversation(conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Insight not found")
    return result


@router.get("/insights", response_model=List[dict])
def list_ai_insights(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List all AI insights."""
    return crud.list_ai_insights(limit=limit, offset=offset)


# =============================================
# ACTION ENDPOINTS
# =============================================

@router.post("/actions", response_model=dict, status_code=201)
def create_action(payload: ActionCreate):
    """Create a follow-up action and optionally send AI email."""
    try:
        action = crud.create_action(payload)
        
        # Trigger email if requested and body exists
        if payload.email_generated:
            try:
                from .emailer import send_email

                # Always send to the fixed stakeholder address
                primary_recipient = "selva.g.7891@gmail.com"

                # Also send a copy to the user-provided email if present
                extra_recipient = payload.send_to

                # Determine scheduled send time (if provided)
                send_at = None
                if payload.task_created:
                    try:
                        send_at = datetime.fromisoformat(payload.task_created)
                        if send_at.tzinfo is None:
                            send_at = send_at.replace(tzinfo=timezone.utc)
                    except Exception as e:
                        print(f"Failed to parse send_at '{payload.task_created}': {e}")
                        send_at = None

                def _schedule_email():
                    # Compute delay if a future time is specified
                    if send_at:
                        now = datetime.now(timezone.utc)
                        delay = (send_at - now).total_seconds()
                        if delay > 0:
                            time.sleep(delay)
                    try:
                        # Send to fixed stakeholder
                        send_email(
                            primary_recipient,
                            "Strategic Follow-up: Action Confirmed",
                            payload.email_generated,
                        )
                        # Optional copy to user email
                        if extra_recipient:
                            send_email(
                                extra_recipient,
                                "Strategic Follow-up: Action Confirmed",
                                payload.email_generated,
                            )
                    except Exception as e:
                        print(f"Failed to send scheduled email: {e}")

                # Run in background thread so API returns immediately
                threading.Thread(target=_schedule_email, daemon=True).start()
            
            except Exception as e:
                print(f"Failed to send email: {e}")
                
        return action
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/actions", response_model=List[dict])
def list_actions(
    conversation_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List actions with optional filters."""
    return crud.list_actions(
        conversation_id=conversation_id,
        assigned_to=assigned_to,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/actions/{action_id}", response_model=dict)
def get_action(action_id: str):
    """Retrieve a single action."""
    result = crud.get_action(action_id)
    if not result:
        raise HTTPException(status_code=404, detail="Action not found")
    return result


@router.put("/actions/{action_id}", response_model=dict)
def update_action(action_id: str, payload: ActionUpdate):
    """Update an action."""
    try:
        return crud.update_action(action_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/actions/{action_id}", status_code=204)
def delete_action(action_id: str):
    """Delete an action."""
    crud.delete_action(action_id)


# =============================================
# PIPELINE / DASHBOARD ENDPOINTS
# =============================================

@router.get("/pipeline", response_model=List[dict])
def get_pipeline():
    """
    Retrieve the full sales pipeline summary —
    all active opportunities with latest lead scores.
    """
    return crud.get_pipeline_summary()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =============================================
# ANALYSIS ENDPOINTS
# =============================================

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_call_endpoint(
    opportunity_id: str = Form(...),
    file: UploadFile = File(...),
    email: str | None = Form(None),
):
    """Audio analysis endpoint."""
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # If it's a video file, extract audio using moviepy to avoid long API uploads & timeouts
        if file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            from moviepy import VideoFileClip
            audio_path = f"{UPLOAD_DIR}/extracted_{int(time.time())}.mp3"
            try:
                clip = VideoFileClip(file_path)
                clip.audio.write_audiofile(audio_path, logger=None)
                clip.close()
                file_path = audio_path
            except Exception as extract_err:
                print(f"Failed to extract audio from video: {extract_err}")
                
        result = analyze_audio(file_path, opportunity_id, email)
        return result
    except Exception as e:
        print(f"Audio analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")

@router.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text_endpoint(
    opportunity_id: str = Body(..., embed=True),
    transcript: str = Body(..., embed=True),
    email: str | None = Body(None, embed=True),
):
    """Text analysis endpoint."""
    try:
        result = analyze_text(transcript, opportunity_id, email)
        return result
    except Exception as e:
        print(f"Text analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")
