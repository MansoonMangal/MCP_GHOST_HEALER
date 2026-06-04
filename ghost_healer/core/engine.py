import logging
import time
from typing import Optional

from ghost_healer.core.config import settings
from ghost_healer.core.cache import cache
from ghost_healer.core.mcp_client import brain_client

logger = logging.getLogger("GhostEngine")


class GhostEngine:
    """
    The orchestrator of AI Healing.
    MCP-first with REST fallback; retry logic for cloud cold starts.
    """

    def __init__(self):
        self.threshold = settings.mcp_server.confidence_threshold
        self.mode = settings.healing.mode

    def get_healed_locator(
        self,
        selector: str,
        action: str,
        dom: str,
        url: Optional[str] = None,
        framework: Optional[str] = None,
    ) -> tuple[Optional[str], float]:
        if settings.healing.cache_enabled:
            cached_selector, cached_confidence = cache.get_with_confidence(selector)
            if cached_selector:
                return cached_selector, cached_confidence

        max_retries = settings.healing.max_retries
        for attempt in range(max_retries):
            try:
                data = brain_client.heal_locator(
                    selector=selector,
                    action=action,
                    dom_snapshot=dom,
                    page_url=url,
                    framework=framework or settings.healing.framework,
                )

                confidence = data.get("confidence") or data.get("confidence_score") or 0.0
                if confidence > 1.0:
                    confidence = confidence / 100.0
                healed = data.get("healed_locator")

                if confidence < self.threshold:
                    return None, confidence

                if self.mode == "strict" and confidence < max(self.threshold, 0.85):
                    return None, confidence

                if settings.healing.cache_enabled and healed:
                    cache.set(selector, healed, confidence)

                return healed, confidence

            except Exception as exc:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * settings.healing.retry_wait_seconds
                    logger.warning(
                        f"Brain unreachable, retrying in {wait}s "
                        f"(attempt {attempt + 1}/{max_retries}): {exc}"
                    )
                    time.sleep(wait)
                    continue
                raise

        return None, 0.0


ghost_engine = GhostEngine()
