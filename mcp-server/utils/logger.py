"""
Structured JSON logger with correlation IDs, timestamps, and file rotation.
Used across all MCP server modules for full observability.
"""
import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Emits each log record as a single JSON line for machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Attach extra fields (e.g. healing_id, test_name passed via 'extra')
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def get_logger(name: str, log_file: str = None, level: str = "INFO") -> logging.Logger:
    """
    Returns a configured logger with console + optional file output.

    Args:
        name:     Module/component name (e.g. 'healing_service')
        log_file: Absolute or relative path for rotating file handler
        level:    Log level string: DEBUG | INFO | WARNING | ERROR
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured — avoid duplicate handlers

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # ── Console handler (human-readable) ──────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # ── File handler (JSON, rotating) ─────────────────────────────────────
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


# ── Module-level helpers ──────────────────────────────────────────────────────

def log_healing_event(logger: logging.Logger, event: dict) -> None:
    """Log a structured healing decision event."""
    logger.info(
        "Healing event",
        extra={
            "event_type": "HEALING_DECISION",
            "healing_id": event.get("healing_id"),
            "original_locator": event.get("original_locator"),
            "healed_locator": event.get("healed_locator"),
            "decision": event.get("decision"),
            "confidence_score": event.get("confidence_score"),
        }
    )


def log_score_breakdown(logger: logging.Logger, healing_id: str, breakdown: dict) -> None:
    """Log the full similarity score breakdown for a healing attempt."""
    logger.debug(
        "Score breakdown",
        extra={"event_type": "SCORE_BREAKDOWN", "healing_id": healing_id, **breakdown}
    )
