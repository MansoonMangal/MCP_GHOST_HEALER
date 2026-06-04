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

        # Eagerly clear/reset mcp_server.log at start of execution
        mcp_log = os.path.join(root_dir, "reports", "logs", "mcp_server.log")
        if os.path.exists(mcp_log):
            try:
                with open(mcp_log, "w", encoding="utf-8") as f:
                    f.write("")
                logger.info("[REPORTER] 🧹 Cleared mcp_server.log for new run")
            except Exception as e:
                logger.warning(f"[REPORTER] Could not clear mcp_server.log: {e}")

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
        page_url: Optional[str] = None,
        line: int = 0,
    ) -> None:
        """
        Log a single healing event with full metadata.
        """
        event: Dict[str, Any] = {
            "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat(),
            "session_id": self.session_id,
            "framework": framework or self.framework,
            "language": "python",
            "file": patched_file,
            "line": line,
            "action": action,
            "old_locator": original,
            "suggested_locator": healed,
            "confidence": round(confidence, 4),
            "page_url": page_url,
            "decision": decision,
            "latency_ms": round(duration_ms, 2),
            "retry_count": retry_count,
            "healing_mode": settings.healing.mode,
        }

        if settings.reporting.save_traces and execution_trace:
            event["execution_trace"] = execution_trace

        self.events.insert(0, event)
        logger.info(
            f"[REPORTER] {action} healed | '{original}' → '{healed}' "
            f"| confidence={confidence:.0%} | decision={decision}"
        )

        # Eagerly flush to a beautiful pretty-printed JSON file
        self._flush_event(event)

    def _flush_event(self, event: Dict[str, Any]) -> None:
        """Eagerly write a beautiful, indented standard JSON session array."""
        live_log = os.path.join(self.output_dir, f"session_{self.session_id}.json")
        try:
            with open(live_log, "w", encoding="utf-8") as f:
                json.dump(self.events, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"[REPORTER] Could not flush event: {e}")

        # Also append to global suggested-fixes.json for cross-language consolidation
        suggested_fixes_path = os.path.join(self.output_dir, "suggested-fixes.json")
        try:
            fixes = []
            if os.path.exists(suggested_fixes_path):
                try:
                    with open(suggested_fixes_path, "r", encoding="utf-8") as f:
                        fixes = json.load(f)
                        if not isinstance(fixes, list):
                            fixes = []
                except Exception:
                    fixes = []
            
            fixes.insert(0, {
                "timestamp": event["timestamp"],
                "framework": event["framework"],
                "language": "python",
                "file": event["file"],
                "line": event["line"],
                "action": event["action"],
                "old_locator": event["old_locator"],
                "suggested_locator": event["suggested_locator"],
                "confidence": event["confidence"],
                "page_url": event["page_url"]
            })
            
            with open(suggested_fixes_path, "w", encoding="utf-8") as f:
                json.dump(fixes, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"[REPORTER] Could not write to suggested-fixes.json: {e}")

    def log_pending_fix(
        self,
        *,
        original: str,
        healed: str,
        confidence: float,
        action: str,
        framework: str,
        page_url: Optional[str],
        file: Optional[str],
        line: int,
    ) -> None:
        """Queue a suggested fix for human approval mode."""
        pending_path = os.path.join(self.output_dir, "pending-fixes.json")
        try:
            rows: List[Dict[str, Any]] = []
            if os.path.exists(pending_path):
                with open(pending_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        rows = loaded

            rows.insert(
                0,
                {
                    "id": f"{self.session_id}-{len(rows)+1}",
                    "timestamp": datetime.now(
                        timezone(timedelta(hours=5, minutes=30))
                    ).isoformat(),
                    "framework": framework,
                    "file": file,
                    "line": line,
                    "action": action,
                    "old_locator": original,
                    "suggested_locator": healed,
                    "confidence": round(confidence, 4),
                    "page_url": page_url,
                    "status": "pending_review",
                },
            )
            with open(pending_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"[REPORTER] Could not write pending fix: {e}")

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
        avg_confidence = sum(e["confidence"] for e in healed) / len(healed) if healed else 0
        avg_latency = sum(e["latency_ms"] for e in self.events) / total

        # Most healed locators
        locator_counts: Dict[str, int] = {}
        for e in self.events:
            loc = e["old_locator"]
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
                "total_files_patched": sum(1 for e in self.events if e.get("file")),
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
