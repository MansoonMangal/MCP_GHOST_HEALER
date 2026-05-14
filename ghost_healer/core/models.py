from pydantic import BaseModel
from typing import Optional, Dict, Any

class HealResult(BaseModel):
    healed_locator: str
    confidence: float
    analysis: Optional[str] = None
    latency_ms: Optional[float] = None
    cached: bool = False
