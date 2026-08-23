from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, time
from enum import Enum

class Sex(str, Enum):
    FEMALE = "female"
    MALE = "male"
    OTHER = "other"
    UNSPECIFIED = "unspecified"

class TimePrecision(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    RANGE = "range"
    UNKNOWN = "unknown"

class BirthProfile(BaseModel):
    id: str
    birth_date: date
    birth_time: Optional[time] = None
    birth_time_precision: TimePrecision
    birth_place_text: str
    timezone: str
    latitude: float
    longitude: float
    sex: Sex
    calendar: str = "gregorian"
    created_at: str
    updated_at: str

class Pillar(BaseModel):
    stem: str
    branch: str

class Chart(BaseModel):
    id: str
    profile_id: str
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Optional[Pillar] = None # Optional for 6-character fallback
    day_master: str
    month_order: str
    hidden_stems: Dict[str, List[str]]
    ten_gods: Dict[str, str]
    five_elements: Dict[str, str]
    yin_yang: Dict[str, str]
    luck_direction: str
    start_of_luck: int
    luck_cycles: List[Dict]
    model_version: str
    created_at: str
