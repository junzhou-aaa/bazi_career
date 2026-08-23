from pydantic import BaseModel
from typing import List, Optional, Dict

class CareerIdentity(BaseModel):
    core_strengths: List[str]
    transferable_skills: List[str]
    technical_skills: List[str]
    domain_skills: List[str]
    evidence: List[str]
    role_families: List[str]
    industry_families: List[str]
    seniority_fit: str
    constraints: List[str]
    gaps: List[str]
    differentiators: List[str]
    narrative: str

class CareerProfile(BaseModel):
    id: str
    profile_id: str
    education: List[Dict]
    experience: List[Dict]
    projects: List[Dict]
    skills: List[str]
    programming: List[str]
    frameworks: List[str]
    cloud: List[str]
    languages: List[str]
    domain_knowledge: List[str]
    communication: List[str]
    leadership: List[str]
    certifications: List[str]
    portfolio_evidence: List[str]
    career_identity: Optional[CareerIdentity] = None
    created_at: str
    updated_at: str

class CareerPlan(BaseModel):
    id: str
    profile_id: str
    content_md: str
    content_json: str
    model_version: str
    prompt_version: str
    taxonomy_version: str
    created_at: str
