from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from ..domain.career.models import CareerPlan
from ..adapters.llm.factory import get_llm_provider
import json
import uuid

class CareerPlanOutput(BaseModel):
    summary: str
    recommended_industries: List[str]
    recommended_roles: List[str]
    skill_gaps: List[str]
    timeline_1_year: str
    timeline_3_year: str
    timeline_5_year: str
    bazi_rationale: str

def run_planning_workflow(profile_id: str, chart_data: dict, career_data: dict, validation_confidence: float) -> CareerPlan:
    """
    Generate a career plan using the Bazi chart and the user's career profile.
    """
    llm = get_llm_provider()
    
    system_prompt = (
        "You are an expert Bazi career strategist. "
        "Create a highly personalized, actionable career plan by synthesizing the user's "
        "Bazi chart (Five Elements, Ten Gods, Luck Cycles) with their real-world skills and experience. "
        "The plan must be practical and tailored to their elemental strengths and upcoming luck cycles."
    )
    
    user_prompt = (
        f"Profile ID: {profile_id}\n"
        f"Validation Confidence Score: {validation_confidence}\n\n"
        f"--- BAZI CHART ---\n"
        f"{json.dumps(chart_data, ensure_ascii=False, indent=2)}\n\n"
        f"--- CAREER PROFILE ---\n"
        f"{json.dumps(career_data, ensure_ascii=False, indent=2)}\n\n"
        "Generate a structured career plan."
    )
    
    plan_output = llm.generate_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_model=CareerPlanOutput
    )
    
    # Generate Markdown format for display/storage
    content_md = f"""# Bazi Career Plan

## Executive Summary
{plan_output.summary}

## Bazi Rationale
{plan_output.bazi_rationale}

## Recommendations
**Industries**: {', '.join(plan_output.recommended_industries)}
**Roles**: {', '.join(plan_output.recommended_roles)}

## Skill Gaps to Address
"""
    for gap in plan_output.skill_gaps:
        content_md += f"- {gap}\n"
        
    content_md += f"""
## Timeline
- **1 Year**: {plan_output.timeline_1_year}
- **3 Years**: {plan_output.timeline_3_year}
- **5 Years**: {plan_output.timeline_5_year}
"""
    
    plan = CareerPlan(
        id=f"plan_{uuid.uuid4().hex[:8]}",
        profile_id=profile_id,
        content_md=content_md,
        content_json=plan_output.model_dump_json(),
        model_version=llm.model if hasattr(llm, 'model') else "unknown",
        prompt_version="1.0.0",
        taxonomy_version="1.0.0",
        created_at=datetime.now().isoformat()
    )
    
    # In a full implementation, we would save the CareerPlan to the database here.
    return plan
