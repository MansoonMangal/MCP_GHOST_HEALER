"""
Ghost Healer — Enhanced Healing Reporter (Phase 8)

Generates structured, per-session JSON reports with full audit trail.
Tracks: selector, healed locator, confidence, decision, retry count,
        framework type, patched file, latency, and execution trace.
"""
import json
import os
import time
import logging
import platform
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from ghost_healer.core.config import settings

logger = logging.getLogger("GhostReporter")


class HealingReporter:
    """
    📊 Enterprise Healing Reporter

    Creates per-run JSON reports in reports/ghost/ with:
    - Full event audit trail
    - Summary statistics
    - Per-framework breakdown
    - Most-healed locators
    """

    def __init__(self):
        # Resolve to workspace root (2 levels up from ghost_healer/utils/reporter.py is project root)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.output_dir = os.path.join(root_dir, settings.reporting.output_dir)
        self.events: List[Dict[str, Any]] = []
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        self.session_id = datetime.now(ist_tz).strftime("%Y%m%d_%H%M%S")
        self.framework = settings.healing.framework
        os.makedirs(self.output_dir, exist_ok=True)

    def log_healing(
        self,
        original: str,
        healed: str,
        confidence: float,
        duration_ms: float,
        *,
        decision: str = "AUTO_HEAL",
        retry_count: int = 0,
        patched_file: Optional[str] = None,
        action: str = "click",
        execution_trace: Optional[Dict] = None,
        framework: Optional[str] = None,
    ) -> None:
        """
        Log a single healing event with full metadata.

        Args:
            original:        The broken locator
            healed:          The AI-healed locator
            confidence:      Confidence score (0.0 - 1.0)
            duration_ms:     Time taken to heal in milliseconds
            decision:        AUTO_HEAL / MANUAL_REVIEW / FAIL
            retry_count:     Number of retries before success
            patched_file:    Source file that was auto-patched (if any)
            action:          Playwright/Selenium action that failed
            execution_trace: Full Brain execution trace (from API response)
            framework:       SDK framework (playwright-python, selenium-java, etc.)
        """
        event: Dict[str, Any] = {
            "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
            "session_id": self.session_id,
            "framework": framework or self.framework,
            "action": action,
            "original_selector": original,
            "healed_selector": healed,
            "confidence_score": round(confidence, 4),
            "decision": decision,
            "latency_ms": round(duration_ms, 2),
            "retry_count": retry_count,
            "patched_file": os.path.basename(patched_file) if patched_file else None,
            "healing_mode": settings.healing.mode,
        }

        if settings.reporting.save_traces and execution_trace:
            event["execution_trace"] = execution_trace

        self.events.append(event)
        logger.info(
            f"[REPORTER] {action} healed | '{original}' → '{healed}' "
            f"| confidence={confidence:.0%} | decision={decision}"
        )

        # Eagerly flush if save_traces is enabled
        if settings.reporting.save_traces:
            self._flush_event(event)

    def _flush_event(self, event: Dict[str, Any]) -> None:
        """Append a single event to the live JSONL log file."""
        live_log = os.path.join(self.output_dir, f"session_{self.session_id}.jsonl")
        try:
            with open(live_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.warning(f"[REPORTER] Could not flush event: {e}")

    def finalize(self) -> Optional[str]:
        """
        Write the final consolidated JSON report for this test session.
        Called automatically via pytest fixture teardown.
        """
        if not self.events:
            return None

        total = len(self.events)
        healed = [e for e in self.events if e["decision"] == "AUTO_HEAL"]
        failed = [e for e in self.events if e["decision"] == "FAIL"]
        avg_confidence = sum(e["confidence_score"] for e in healed) / len(healed) if healed else 0
        avg_latency = sum(e["latency_ms"] for e in self.events) / total

        # Most healed locators
        locator_counts: Dict[str, int] = {}
        for e in self.events:
            loc = e["original_selector"]
            locator_counts[loc] = locator_counts.get(loc, 0) + 1
        top_locators = sorted(
            locator_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        report = {
            "meta": {
                "session_id": self.session_id,
                "generated_at": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
                "framework": self.framework,
                "healing_mode": settings.healing.mode,
                "platform": platform.system(),
                "brain_url": settings.mcp_server.url,
            },
            "summary": {
                "total_healing_attempts": total,
                "auto_healed": len(healed),
                "failed_to_heal": len(failed),
                "success_rate_percent": round(len(healed) / total * 100, 1) if total else 0,
                "average_confidence": round(avg_confidence, 4),
                "average_latency_ms": round(avg_latency, 2),
                "total_files_patched": sum(1 for e in self.events if e.get("patched_file")),
            },
            "top_unstable_locators": [
                {"selector": loc, "failure_count": cnt} for loc, cnt in top_locators
            ],
            "events": self.events,
        }

        report_file = os.path.join(
            self.output_dir, f"report_{self.session_id}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(
            f"[REPORTER] 📄 Report saved → {report_file} "
            f"({len(healed)}/{total} healed, avg confidence={avg_confidence:.0%})"
        )
        return report_file


# Global instance
reporter = HealingReporter()
