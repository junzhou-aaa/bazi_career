from typing import List
from datetime import datetime
from pydantic import BaseModel
from ..domain.validation.models import CalibrationRecord
from ..adapters.llm.factory import get_llm_provider
import json

class ValidationResponse(BaseModel):
    calibrations: List[CalibrationRecord]
    confidence_score: float
    summary: str

def run_validation_workflow(profile_id: str, chart_data: dict, career_data: dict) -> ValidationResponse:
    """
    Run the historical validation workflow.
    Compares the generated Bazi chart with the user's real-world career profile
    to generate calibration records and a confidence score.
    """
    llm = get_llm_provider()
    
    system_prompt = (
        "You are an expert Bazi (Four Pillars of Destiny) astrologer and career consultant. "
        "Your task is to validate a user's Bazi chart against their actual career history. "
        "Identify historical correlations between their luck cycles (Da Yun) or annual pillars "
        "and their real-world job changes, promotions, or challenges. "
        "Generate calibration records with prior and posterior confidence scores based on the evidence."
    )
    
    user_prompt = (
        f"Profile ID: {profile_id}\n\n"
        f"--- BAZI CHART ---\n"
        f"{json.dumps(chart_data, ensure_ascii=False, indent=2)}\n\n"
        f"--- CAREER HISTORY ---\n"
        f"{json.dumps(career_data, ensure_ascii=False, indent=2)}\n\n"
        "Please analyze the correlations and return the structured validation data."
    )
    
    # We ask the LLM to output our ValidationResponse structure directly
    response = llm.generate_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=ValidationResponse
    )
    
    # In a full implementation, we would save the calibration records to the database here.
    return response
