import logging
import httpx
from typing import Optional
from ghost_healer.core.config import settings
from ghost_healer.core.cache import cache

logger = logging.getLogger("GhostEngine")

class GhostEngine:
    """ 
    The orchestrator of AI Healing.
    Consults cache, communicates with Brain, and triggers source patching.
    """
    def __init__(self): 
        self.server_url = settings.mcp_server.url
        self.threshold = settings.mcp_server.confidence_threshold
        self.mode = settings.healing.mode

    def get_healed_locator(self, selector: str, action: str, dom: str) -> Optional[str]:
        # 1. Check Cache First
        if settings.healing.cache_enabled:
            cached = cache.get(selector)
            if cached:
                logger.info(f"✨ [CACHE HIT] Found healed locator: {cached}")
                return cached

        # 2. Consult the AI Brain
        logger.info(f"🧠 [AI BRAIN] Analyzing failure for: {selector}")
        try:
            with httpx.Client(timeout=settings.mcp_server.timeout) as client:
                response = client.post(
                    f"{self.server_url}/api/heal-locator",
                    json={
                        "selector": selector,
                        "action": action,
                        "dom_snapshot": dom
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    confidence = data.get("confidence", 0)
                    healed = data.get("healed_locator")

                    if confidence >= self.threshold:
                        # 3. Store in Cache
                        if settings.healing.cache_enabled:
                            cache.set(selector, healed, confidence)
                        return healed
        except Exception as e:
            logger.error(f"Brain communication failure: {e}")
            
        return None

# Global engine instance
ghost_engine = GhostEngine()
