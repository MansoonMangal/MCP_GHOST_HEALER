from dataclasses import dataclass
from typing import Optional

@dataclass
class HealResult:
    """Standard model for all healing results."""
    healed_locator: str
    confidence_score: float
    analysis_time_ms: float
    found_via: str  # 'ai', 'cache', 'dna'
    failure_reason: Optional[str] = None
