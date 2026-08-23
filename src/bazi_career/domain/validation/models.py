from pydantic import BaseModel
from typing import List, Optional

class Prediction(BaseModel):
    id: str
    profile_id: str
    period: str
    domain: str
    claim: str
    traditional_rationale: str
    confidence: float
    alternative_explanations: List[str]
    created_at: str

class ValidationEvent(BaseModel):
    id: str
    prediction_id: str
    outcome: str # occurred, partially_occurred, did_not_occur, unknown
    evidence_statement: str
    created_at: str

class CalibrationRecord(BaseModel):
    id: str
    profile_id: str
    hypothesis: str
    evidence_ids: List[str]
    prior_confidence: float
    posterior_confidence: float
    support: List[str]
    counterevidence: List[str]
    notes: Optional[str] = None
    created_at: str
