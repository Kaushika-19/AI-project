import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class SuggestionSchema(BaseModel):
    title: str
    next_best_action: str
    confidence_level_0_to_1: float
    risk_level: str
    next_reminder_date: str
    reasoning: str
    email_draft: str

class RecommendationSchema(BaseModel):
    suggestions: List[SuggestionSchema]

print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

parser = PydanticOutputParser(pydantic_object=RecommendationSchema)
prompt = PromptTemplate(
    template="Suggest 3 sales actions for: {data}\n{format_instructions}",
    input_variables=["data"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

try:
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    chain = prompt | model | parser
    res = chain.invoke({"data": "Customer wants a demo but is worried about price."})
    print("SUCCESS")
    print(res)
except Exception as e:
    print("FAILURE")
    print(f"Error Type: {type(e)}")
    print(f"Error Message: {e}")
