"""
Healing Reporter — pytest plugin that captures healing events per test
and writes structured JSON reports to the reports/logs/ directory.

Registered automatically via conftest.py.
"""
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytest

logger = logging.getLogger("healing_reporter")

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports" / "logs"


@dataclass
class HealingEvent:
    test_name: str
    original_locator: str
    healed_locator: Optional[str]
    confidence_score: float
    confidence_level: str
    decision: str
    was_healed: bool
    healing_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TestReport:
    test_name: str
    status: str         # PASSED | FAILED | SKIPPED
    duration_ms: float
    healing_events: List[HealingEvent] = field(default_factory=list)
    total_healed: int = 0
    total_failed_heals: int = 0
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HealingReporter:
    """
    Pytest plugin that tracks healing events and writes per-run JSON reports.
    Test functions store healing results in pytest.current_healing_events list.
    """

    def __init__(self):
        self.reports: List[TestReport] = []
        self._current: Optional[TestReport] = None
        self._start_time: float = 0.0

    # ── Pytest hooks ───────────────────────────────────────────────────────

    def pytest_runtest_setup(self, item):
        self._current = TestReport(test_name=item.nodeid, status="RUNNING", duration_ms=0.0)
        self._start_time = time.monotonic()
        # Inject a mutable list into the test's namespace for collecting events
        item._healing_events = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call" and self._current:
            duration = (time.monotonic() - self._start_time) * 1000
            self._current.duration_ms = round(duration, 2)
            self._current.status = "PASSED" if report.passed else "FAILED" if report.failed else "SKIPPED"

    def pytest_runtest_teardown(self, item, nextitem):
        if self._current:
            # Collect healing events attached by test
            events: List[HealingEvent] = getattr(item, "_healing_events", [])
            self._current.healing_events = events
            self._current.total_healed = sum(1 for e in events if e.was_healed)
            self._current.total_failed_heals = sum(1 for e in events if not e.was_healed)
            self.reports.append(self._current)
            self._current = None

    def pytest_sessionfinish(self, session, exitstatus):
        self._write_report()

    # ── Report writer ──────────────────────────────────────────────────────

    def _write_report(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = REPORTS_DIR / f"healing_report_{timestamp}.json"

        summary = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.reports),
            "total_passed": sum(1 for r in self.reports if r.status == "PASSED"),
            "total_failed": sum(1 for r in self.reports if r.status == "FAILED"),
            "total_healing_events": sum(len(r.healing_events) for r in self.reports),
            "total_auto_healed": sum(r.total_healed for r in self.reports),
            "tests": [asdict(r) for r in self.reports],
        }

        report_file.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        logger.info(f"Healing report written to: {report_file}")
        print(f"\nHealing Report: {report_file}")


def attach_healing_event(request: pytest.FixtureRequest, event: HealingEvent) -> None:
    """Helper called from tests to register a healing event with the reporter."""
    if hasattr(request.node, "_healing_events"):
        request.node._healing_events.append(event)
