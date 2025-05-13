from pydantic import BaseModel
from typing import Optional, Dict

class PropertyAnalysisRequest(BaseModel):
    zip: str
    budget: float
    preferences: Optional[Dict] = {}
