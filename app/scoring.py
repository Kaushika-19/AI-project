import re
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class AnalysisSchema(BaseModel):
    conversation_summary: str = Field(description="Max 2 sentences summary")
    interest_score: int = Field(description="0-100 score", ge=0, le=100)
    interest_signals: List[str] = Field(description="Key positive signals")
    trust_score: int = Field(description="0-100 score", ge=0, le=100)
    trust_signals: List[str] = Field(description="Trust markers")
    sentiment: str = Field(description="Positive, Neutral, or Negative")
    sentiment_compound: float = Field(description="-1 to 1 float")
    objections: List[str] = Field(description="List of objections")
    objection_count: int = Field(description="Count of objections")
    buying_stage: str = Field(description="DISCOVERY, EVALUATION, NEGOTIATION, PROPOSAL, or CLOSING")
    urgency_level: str = Field(description="High, Medium, or Low")
    conversion_probability: int = Field(description="0-100 probability")

def analyze_call(
    transcript: str,
    speaker_turns: Optional[List[Tuple[str, str]]] = None
) -> Dict[str, Any]:
    """
    AI-powered core analysis of a sales conversation using LangChain.
    """
    
    if not transcript or len(transcript.strip()) < 10:
        return {
            "conversation_summary": "Incomplete interaction transcript.",
            "interest": {"interest_score_0_100": 10, "signals": {}},
            "trust": {"trust_score_0_100": 50, "signals": {}},
            "sentiment": {"sentiment": "Neutral", "sentiment_compound": 0.0},
            "objections": {"objections": [], "objection_count": 0},
            "buying_stage": {"buying_stage": "DISCOVERY", "stage_scores": {}},
            "urgency": {"urgency_level": "Low", "urgency_hits": 0},
            "conversion_score_0_100": 10.0
        }

    turns_context = ""
    if speaker_turns:
        turns_context = "\n".join([f"{sp}: {txt}" for sp, txt in speaker_turns])
    else:
        turns_context = transcript

    parser = PydanticOutputParser(pydantic_object=AnalysisSchema)

    prompt = PromptTemplate(
        template=(
            "You are an expert B2B sales coach.\n"
            "{format_instructions}\n\n"
            "Analyze this sales conversation in depth and return highly detailed insights.\n"
            "- Be specific in interest_signals and trust_signals (short bullet-like phrases).\n"
            "- List every clear objection you detect in objections.\n"
            "- Pick the most accurate buying_stage based on the whole call.\n"
            "- Set urgency_level based on deadlines, pressure, or timelines discussed.\n\n"
            "Conversation:\n{conversation}\n"
        ),
        input_variables=["conversation"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # larger, more capable model for richer insights
            google_api_key=api_key,
            temperature=0.2
        )
        
        chain = prompt | model | parser
        result = chain.invoke({"conversation": turns_context})

        # Map back to expected structure
        return {
            "conversation_summary": result.conversation_summary,
            "interest": {
                "interest_score_0_100": result.interest_score,
                "signals": result.interest_signals
            },
            "trust": {
                "trust_score_0_100": result.trust_score,
                "signals": result.trust_signals
            },
            "sentiment": {
                "sentiment": result.sentiment,
                "sentiment_compound": result.sentiment_compound
            },
            "objections": {
                "objections": result.objections,
                "objection_count": result.objection_count
            },
            "buying_stage": {"buying_stage": result.buying_stage.upper()},
            "urgency": {"urgency_level": result.urgency_level},
            "conversion_score_0_100": float(result.conversion_probability)
        }

    except Exception as e:
        print(f"LangChain Analysis Error: {e}")
        # Baseline fallback
        return {
            "conversation_summary": f"Analysis service failed: {e}",
            "interest": {"interest_score_0_100": 50, "signals": []},
            "trust": {"trust_score_0_100": 50, "signals": []},
            "sentiment": {"sentiment": "Neutral", "sentiment_compound": 0.0},
            "objections": {"objections": [], "objection_count": 0},
            "buying_stage": {"buying_stage": "DISCOVERY"},
            "urgency": {"urgency_level": "Medium"},
            "conversion_score_0_100": 50.0
        }
