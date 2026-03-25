"""
CRUD Operations — Supabase Data Access Layer
=============================================
All database operations for the Sales Intelligence system.
Uses the Supabase Python client to interact with the Postgres database.
"""

from __future__ import annotations

from typing import List, Optional, Any
from datetime import date

from .db import supabase
from .models import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    OpportunityCreate, OpportunityUpdate, OpportunityResponse,
    ConversationCreate, ConversationResponse,
    AIInsightCreate, AIInsightResponse,
    ActionCreate, ActionUpdate, ActionResponse,
)


def _get_data(result: Any) -> Any:
    """
    Safely unwrap Supabase responses across client versions.
    Handles objects with `.data`, plain dicts, or None.
    """
    if result is None:
        return None
    if isinstance(result, dict):
        return result.get("data")
    return getattr(result, "data", None)


# =============================================
# CUSTOMERS
# =============================================

def create_customer(data: CustomerCreate) -> dict:
    """Insert a new customer. If email already exists, update and return the customer."""
    existing = get_customer_by_email(data.email)

    payload = data.model_dump(mode="json")
    if existing:
        # Update existing customer with new details
        return update_customer(existing["customer_id"], CustomerUpdate(**payload))

    result = (
        supabase.table("customers")
        .insert(payload)
        .execute()
    )
    data_payload = _get_data(result)
    if not data_payload:
        raise ValueError("Failed to create customer in database.")
    return data_payload[0]


def get_customer(customer_id: str) -> Optional[dict]:
    """Retrieve a single customer by ID."""
    result = (
        supabase.table("customers")
        .select("*")
        .eq("customer_id", customer_id)
        .single()
        .execute()
    )
    return _get_data(result)


def get_customer_by_email(email: str) -> Optional[dict]:
    """Retrieve a customer by their email address."""
    result = (
        supabase.table("customers")
        .select("*")
        .eq("email", email)
        .maybe_single()
        .execute()
    )
    return _get_data(result)


def list_customers(limit: int = 50, offset: int = 0) -> List[dict]:
    """List customers with pagination."""
    result = (
        supabase.table("customers")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return _get_data(result) or []


def update_customer(customer_id: str, data: CustomerUpdate) -> dict:
    """Update an existing customer."""
    update_data = data.model_dump(mode="json", exclude_none=True)
    result = (
        supabase.table("customers")
        .update(update_data)
        .eq("customer_id", customer_id)
        .execute()
    )
    return result.data[0]


def delete_customer(customer_id: str) -> bool:
    """Delete a customer (cascades to all related records)."""
    supabase.table("customers").delete().eq("customer_id", customer_id).execute()
    return True


# =============================================
# OPPORTUNITIES
# =============================================

def create_opportunity(data: OpportunityCreate) -> dict:
    """Insert a new sales opportunity."""
    payload = data.model_dump(mode="json")
    # Convert enums to their string values
    if payload.get("stage"):
        payload["stage"] = payload["stage"]
    if payload.get("status"):
        payload["status"] = payload["status"]
    # Convert date objects to strings
    if payload.get("expected_close_date"):
        payload["expected_close_date"] = str(payload["expected_close_date"])

    result = (
        supabase.table("opportunities")
        .insert(payload)
        .execute()
    )
    return result.data[0]


def get_opportunity(opportunity_id: str) -> Optional[dict]:
    """Retrieve a single opportunity by ID."""
    result = (
        supabase.table("opportunities")
        .select("*")
        .eq("opportunity_id", opportunity_id)
        .single()
        .execute()
    )
    return result.data


def list_opportunities(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    stage: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[dict]:
    """List opportunities with optional filters."""
    query = supabase.table("opportunities").select("*")
    if customer_id:
        query = query.eq("customer_id", customer_id)
    if status:
        query = query.eq("status", status)
    if stage:
        query = query.eq("stage", stage)
    result = query.order("last_updated", desc=True).range(offset, offset + limit - 1).execute()
    return result.data


def update_opportunity(opportunity_id: str, data: OpportunityUpdate) -> dict:
    """Update an opportunity (stage, status, etc.)."""
    update_data = data.model_dump(mode="json", exclude_none=True)
    # Convert date objects to strings
    for date_field in ("expected_close_date", "closed_date"):
        if date_field in update_data and isinstance(update_data[date_field], date):
            update_data[date_field] = str(update_data[date_field])

    result = (
        supabase.table("opportunities")
        .update(update_data)
        .eq("opportunity_id", opportunity_id)
        .execute()
    )

    # Automatically close/cancel associated actions when the deal is closed
    new_status = update_data.get("status")
    if result.data and new_status in ("CLOSED_WON", "CLOSED_LOST", "DISQUALIFIED"):
        try:
            # 1. Get all conversations linked to this opportunity
            convs = supabase.table("conversations").select("conversation_id").eq("opportunity_id", opportunity_id).execute()
            conv_ids = [c["conversation_id"] for c in convs.data]
            
            if conv_ids:
                # 2. Determine appropriate action status
                target_action_status = "COMPLETED" if new_status == "CLOSED_WON" else "CANCELLED"
                
                # 3. Update all PENDING or IN_PROGRESS actions for these conversations
                supabase.table("actions").update({"status": target_action_status})\
                    .in_("conversation_id", conv_ids)\
                    .neq("status", "COMPLETED")\
                    .neq("status", "CANCELLED")\
                    .execute()
        except Exception as e:
            print(f"Background update for actions failed: {e}")

    return result.data[0] if result.data else {}


def delete_opportunity(opportunity_id: str) -> bool:
    """Delete an opportunity."""
    supabase.table("opportunities").delete().eq("opportunity_id", opportunity_id).execute()
    return True


# =============================================
# CONVERSATIONS
# =============================================

def create_conversation(data: ConversationCreate) -> dict:
    """Insert a new conversation record."""
    payload = data.model_dump(mode="json")
    result = (
        supabase.table("conversations")
        .insert(payload)
        .execute()
    )
    return result.data[0]


def get_conversation(conversation_id: str) -> Optional[dict]:
    """Retrieve a single conversation by ID."""
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("conversation_id", conversation_id)
        .single()
        .execute()
    )
    return result.data


def list_conversations(
    opportunity_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[dict]:
    """List conversations with optional filters."""
    query = supabase.table("conversations").select("*")
    if opportunity_id:
        query = query.eq("opportunity_id", opportunity_id)
    if customer_id:
        query = query.eq("customer_id", customer_id)
    if source:
        query = query.eq("source", source)
    result = query.order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
    return result.data


def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation (cascades to insights + actions)."""
    supabase.table("conversations").delete().eq("conversation_id", conversation_id).execute()
    return True


# =============================================
# AI INSIGHTS
# =============================================

def create_ai_insight(data: AIInsightCreate) -> dict:
    """Insert an AI insight for a conversation."""
    payload = data.model_dump(mode="json")
    result = (
        supabase.table("ai_insights")
        .insert(payload)
        .execute()
    )
    return result.data[0]


def get_ai_insight_by_conversation(conversation_id: str) -> Optional[dict]:
    """Retrieve the AI insight for a specific conversation."""
    result = (
        supabase.table("ai_insights")
        .select("*")
        .eq("conversation_id", conversation_id)
        .maybe_single()
        .execute()
    )
    return result.data


def list_ai_insights(limit: int = 50, offset: int = 0) -> List[dict]:
    """List all AI insights."""
    result = (
        supabase.table("ai_insights")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data


# =============================================
# ACTIONS
# =============================================

def create_action(data: ActionCreate) -> dict:
    """Insert a follow-up action. Excludes non-schema fields like send_to."""
    payload = data.model_dump(mode="json")
    
    # Remove fields used for business logic but not stored in DB
    payload.pop("send_to", None)
    
    if payload.get("deadline"):
        payload["deadline"] = str(payload["deadline"])
        
    result = (
        supabase.table("actions")
        .insert(payload)
        .execute()
    )
    return result.data[0]


def get_action(action_id: str) -> Optional[dict]:
    """Retrieve a single action by ID."""
    result = (
        supabase.table("actions")
        .select("*")
        .eq("action_id", action_id)
        .single()
        .execute()
    )
    return result.data


def list_actions(
    conversation_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[dict]:
    """List actions with optional filters."""
    query = supabase.table("actions").select("*")
    if conversation_id:
        query = query.eq("conversation_id", conversation_id)
    if assigned_to:
        query = query.eq("assigned_to", assigned_to)
    if status:
        query = query.eq("status", status)
    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return result.data


def update_action(action_id: str, data: ActionUpdate) -> dict:
    """Update an action's status, assignee, etc."""
    update_data = data.model_dump(mode="json", exclude_none=True)
    if "deadline" in update_data and isinstance(update_data["deadline"], date):
        update_data["deadline"] = str(update_data["deadline"])

    result = (
        supabase.table("actions")
        .update(update_data)
        .eq("action_id", action_id)
        .execute()
    )
    return result.data[0]


def delete_action(action_id: str) -> bool:
    """Delete an action."""
    supabase.table("actions").delete().eq("action_id", action_id).execute()
    return True


# =============================================
# COMPOSITE QUERIES
# =============================================

def get_customer_history(customer_id: str) -> dict:
    """
    Retrieve full customer history:
      customer → opportunities → conversations → ai_insights + actions
    """
    customer = get_customer(customer_id)
    if not customer:
        return None

    opportunities = list_opportunities(customer_id=customer_id, limit=100)
    enriched_opportunities = []

    for opp in opportunities:
        conversations = list_conversations(
            opportunity_id=opp["opportunity_id"], limit=200
        )
        enriched_convos = []
        for conv in conversations:
            insight = get_ai_insight_by_conversation(conv["conversation_id"])
            actions_list = list_actions(conversation_id=conv["conversation_id"])
            action = actions_list[0] if actions_list else None
            enriched_convos.append({
                "conversation": conv,
                "ai_insight": insight,
                "action": action,
            })

        enriched_opportunities.append({
            "opportunity": opp,
            "conversations": enriched_convos,
        })

    return {
        "customer": customer,
        "opportunities": enriched_opportunities,
    }


def get_opportunity_timeline(opportunity_id: str) -> dict:
    """
    Get the full conversation timeline for an opportunity,
    showing how the deal progressed through stages.
    """
    opportunity = get_opportunity(opportunity_id)
    if not opportunity:
        return None

    conversations = list_conversations(opportunity_id=opportunity_id, limit=200)
    timeline = []

    for conv in conversations:
        insight = get_ai_insight_by_conversation(conv["conversation_id"])
        actions_list = list_actions(conversation_id=conv["conversation_id"])
        action = actions_list[0] if actions_list else None
        timeline.append({
            "conversation": conv,
            "ai_insight": insight,
            "action": action,
        })

    return {
        "opportunity": opportunity,
        "timeline": timeline,
    }


def get_pipeline_summary() -> List[dict]:
    """Retrieve the opportunity pipeline summary view."""
    result = (
        supabase.table("opportunities")
        .select("*, customers(name)")
        .execute()
    )
    
    pipeline = []
    if result.data:
        for row in result.data:
            customer_data = row.pop("customers", {})
            if isinstance(customer_data, list):
                customer_name = customer_data[0].get("name", "Unknown") if customer_data else "Unknown"
            elif isinstance(customer_data, dict):
                customer_name = customer_data.get("name", "Unknown")
            else:
                customer_name = "Unknown"
                
            row["customer_name"] = customer_name
            pipeline.append(row)
            
    return pipeline
