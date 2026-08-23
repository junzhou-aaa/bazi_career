from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    id: str
    company_id: str
    title: str
    role_family: str
    seniority: str
    location: str
    remote_preference: str
    work_authorization_required: bool
    sponsorship_available: Optional[bool] = None
    description: str
    source: str
    source_url: str
    source_last_verified_at: str
    created_at: str
    updated_at: str

class JobMatch(BaseModel):
    id: str
    job_id: str
    profile_id: str
    role_fit_score: float
    skill_fit_score: float
    industry_fit_score: float
    seniority_fit_score: float
    location_fit_score: float
    work_authorization_fit_score: float
    company_fit_score: float
    narrative_fit_score: float
    total_score: float
    tier: str # Tier 1, Tier 2, Opportunity, Safety
    rationale: str
    evidence_tier: str # verified_primary_source, inferred, etc.
    created_at: str
