import json
import os
import time
import logging
from datetime import datetime
from ghost_healer.core.config import settings

logger = logging.getLogger("GhostReporter")

class HealingReporter:
    """
    📊 ENTERPRISE REPORTER:
    Generates structured JSON logs and execution traces for all healing events.
    """
    def __init__(self):
        self.output_dir = settings.reporting.output_dir
        self.events = []
        os.makedirs(self.output_dir, exist_ok=True)

    def log_healing(self, original: str, healed: str, confidence: float, duration: float):
        event = {
            "timestamp": datetime.now().isoformat(),
            "original_selector": original,
            "healed_selector": healed,
            "confidence_score": confidence,
            "latency_ms": duration,
            "mode": settings.healing.mode
        }
        self.events.append(event)
        logger.info(f"📊 [REPORTED] Heal event saved for {original}")

    def finalize(self):
        if not self.events:
            return

        report_file = os.path.join(
            self.output_dir, 
            f"healing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        summary = {
            "total_heals": len(self.events),
            "average_confidence": sum(e["confidence_score"] for e in self.events) / len(self.events),
            "events": self.events
        }
        
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=4)
            
        logger.info(f"📄 [REPORT GENERATED] {report_file}")

# Global reporter instance
reporter = HealingReporter()
