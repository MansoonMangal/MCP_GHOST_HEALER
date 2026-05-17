"""
Structured JSON logger with correlation IDs, timestamps, and file rotation.
Used across all MCP server modules for full observability.
"""
import logging
import logging.handlers
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


class ReadableFormatter(logging.Formatter):
    """Emits each log record as a beautiful, human-readable standard log line in IST (+05:30)."""

    def format(self, record: logging.LogRecord) -> str:
        # Calculate IST time (+05:30)
        from datetime import datetime, timedelta, timezone
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        ist_now = datetime.now(ist_tz)
        dt_str = ist_now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Format base log string
        base = f"[{dt_str} +05:30] [{record.levelname:<7}] [{record.name:<18}] {record.getMessage()}"

        # Append true custom metadata (excluding standard Python LogRecord attributes)
        STANDARD_FIELDS = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'taskName', 'asctime', 'message'
        }
        extras = []
        for key, value in record.__dict__.items():
            if key not in STANDARD_FIELDS and not key.startswith("_"):
                extras.append(f"{key}={value}")
        if extras:
            base += f"  ➔  ({', '.join(extras)})"

        # Append stack traces / exceptions if any
        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


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
        file_handler.setFormatter(ReadableFormatter())
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
