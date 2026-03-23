"""
Pydantic Models for Sales Conversation Intelligence
====================================================
Defines request/response schemas for all 5 core entities:
  - Customers
  - Opportunities
  - Conversations
  - AI Insights
  - Actions
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# =============================================
# ENUMS (mirror Postgres enum types)
# =============================================

class OpportunityStatus(str, Enum):
    OPEN         = "OPEN"
    IN_PROGRESS  = "IN_PROGRESS"
    ON_HOLD      = "ON_HOLD"
    CLOSED_WON   = "CLOSED_WON"
    CLOSED_LOST  = "CLOSED_LOST"
    DISQUALIFIED = "DISQUALIFIED"


class SalesStage(str, Enum):
    LEAD          = "LEAD"
    DISCOVERY     = "DISCOVERY"
    EVALUATION    = "EVALUATION"
    CONSIDERATION = "CONSIDERATION"
    NEGOTIATION   = "NEGOTIATION"
    PROPOSAL      = "PROPOSAL"
    CLOSING       = "CLOSING"


class ConversationSource(str, Enum):
    CALL    = "call"
    CHAT    = "chat"
    EMAIL   = "email"
    MEETING = "meeting"


class ActionStatus(str, Enum):
    PENDING     = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED   = "COMPLETED"
    CANCELLED   = "CANCELLED"


class Sentiment(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL  = "Neutral"


class Urgency(str, Enum):
    LOW    = "Low"
    MEDIUM = "Medium"
    HIGH   = "High"


# =============================================
# CUSTOMER MODELS
# =============================================

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    company: str
    industry: Optional[str] = None
    company_size: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    company: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    created_at: datetime


# =============================================
# OPPORTUNITY MODELS
# =============================================

class OpportunityCreate(BaseModel):
    customer_id: str
    opportunity_name: str
    product_interest: Optional[str] = None
    deal_value: Optional[float] = Field(default=0.00, ge=0)
    stage: SalesStage = SalesStage.LEAD
    status: OpportunityStatus = OpportunityStatus.OPEN
    probability: Optional[float] = Field(default=0.00, ge=0, le=100)
    assigned_sales_rep: Optional[str] = None
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class OpportunityUpdate(BaseModel):
    opportunity_name: Optional[str] = None
    product_interest: Optional[str] = None
    deal_value: Optional[float] = Field(default=None, ge=0)
    stage: Optional[SalesStage] = None
    status: Optional[OpportunityStatus] = None
    probability: Optional[float] = Field(default=None, ge=0, le=100)
    assigned_sales_rep: Optional[str] = None
    expected_close_date: Optional[date] = None
    closed_date: Optional[date] = None
    notes: Optional[str] = None


class OpportunityResponse(BaseModel):
    opportunity_id: str
    customer_id: str
    opportunity_name: str
    product_interest: Optional[str] = None
    deal_value: float
    stage: str
    status: str
    probability: float
    assigned_sales_rep: Optional[str] = None
    expected_close_date: Optional[date] = None
    closed_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    last_updated: datetime


# =============================================
# CONVERSATION MODELS
# =============================================

class ConversationCreate(BaseModel):
    opportunity_id: str
    customer_id: str
    transcript: str
    source: ConversationSource = ConversationSource.CALL


class ConversationResponse(BaseModel):
    conversation_id: str
    opportunity_id: str
    customer_id: str
    transcript: str
    source: str
    timestamp: datetime


# =============================================
# AI INSIGHT MODELS
# =============================================

class AIInsightCreate(BaseModel):
    conversation_id: str
    intent: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    lead_score: Optional[float] = Field(default=0.00, ge=0, le=100)
    objection: Optional[str] = None
    stage_detected: Optional[SalesStage] = None
    urgency: Optional[Urgency] = None
    confidence: Optional[float] = Field(default=0.00, ge=0, le=1)


class AIInsightResponse(BaseModel):
    insight_id: str
    conversation_id: str
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    lead_score: Optional[float] = None
    objection: Optional[str] = None
    stage_detected: Optional[str] = None
    urgency: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime


# =============================================
# ACTION MODELS
# =============================================

class ActionCreate(BaseModel):
    conversation_id: str
    next_best_action: str
    email_generated: Optional[str] = None
    task_created: Optional[str] = None
    assigned_to: Optional[str] = None
    deadline: Optional[date] = None
    status: ActionStatus = ActionStatus.PENDING
    send_to: Optional[str] = None # Optional email recipient


class ActionUpdate(BaseModel):
    next_best_action: Optional[str] = None
    email_generated: Optional[str] = None
    task_created: Optional[str] = None
    assigned_to: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[ActionStatus] = None


class ActionResponse(BaseModel):
    action_id: str
    conversation_id: str
    next_best_action: str
    email_generated: Optional[str] = None
    task_created: Optional[str] = None
    assigned_to: Optional[str] = None
    deadline: Optional[date] = None
    status: str
    created_at: datetime


# =============================================
# COMPOSITE RESPONSE MODELS
# =============================================

class CustomerHistory(BaseModel):
    """Full customer history including opportunities, conversations, and insights."""
    customer: CustomerResponse
    opportunities: List[OpportunityWithConversations]


class OpportunityWithConversations(BaseModel):
    """Opportunity with all its conversations and associated AI insights/actions."""
    opportunity: OpportunityResponse
    conversations: List[ConversationDetail]


class ConversationDetail(BaseModel):
    """Conversation with linked AI insight and action."""
    conversation: ConversationResponse
    ai_insight: Optional[AIInsightResponse] = None
    action: Optional[ActionResponse] = None


class AnalysisResponse(BaseModel):
    """Response from the AI analysis pipeline."""
    conversation_id: str
    transcript: str
    analysis: dict
    email_preview: str
    action_suggested: str
    deadline: str
    suggestions: List[dict] = []


# Rebuild forward refs so nested models resolve
CustomerHistory.model_rebuild()
OpportunityWithConversations.model_rebuild()