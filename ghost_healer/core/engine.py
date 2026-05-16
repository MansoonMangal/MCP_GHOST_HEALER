import logging
import httpx
import time
from typing import Optional
from ghost_healer.core.config import settings
from ghost_healer.core.cache import cache
from ghost_healer.utils.source_healer import source_healer

logger = logging.getLogger("GhostEngine")

class GhostEngine:
    """
    The orchestrator of AI Healing.
    Optimized for Cloud/SaaS deployments with retry logic and caching.
    """
    def __init__(self):
        self.server_url = settings.mcp_server.url
        self.threshold = settings.mcp_server.confidence_threshold
        self.mode = settings.healing.mode

    def get_healed_locator(self, selector: str, action: str, dom: str, url: Optional[str] = None, framework: Optional[str] = None) -> Optional[str]:
        # 1. Check Cache
        if settings.healing.cache_enabled:
            cached = cache.get(selector)
            if cached:
                return cached

        # 2. Consult Brain with Retry (For Cloud Cold Starts)
        max_retries = settings.healing.max_retries
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=settings.mcp_server.timeout) as client:
                    payload = {
                        "selector": selector,
                        "action": action,
                        "dom_snapshot": dom,
                        "page_url": url,
                        "framework": framework or settings.healing.framework
                    }
                    response = client.post(
                        f"{self.server_url}/api/heal-locator",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        confidence = data.get("confidence", 0)
                        healed = data.get("healed_locator")

                        if confidence < self.threshold:
                            return None

                        if self.mode == "suggestion":
                            return None
                        
                        if settings.healing.cache_enabled:
                            cache.set(selector, healed, confidence)
                        
                        if settings.healing.auto_patch:
                            source_healer.apply_fix(selector, healed)
                            
                        return healed
                    
            except (httpx.ConnectError, httpx.TimeoutException):
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * settings.healing.retry_wait_seconds
                    logger.warning(f"☁️ Cloud Brain is waking up... retrying in {wait}s (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                raise

        return None

# Global engine instance
ghost_engine = GhostEngine()
