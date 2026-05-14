import logging
from typing import Dict, Any, Optional, Tuple
from playwright.sync_api import Page, Locator
from ghost_framework.wrappers.api_client import api_client
from ghost_framework.wrappers.models import HealResult

logger = logging.getLogger("SafeLocator")

class SafeLocator:
    """
    The Core Intelligence for finding and healing elements.
    """
    def __init__(self, page: Page):
        self.page = page

    def locate(self, selector: str, action: str = "click", hints: Dict = None) -> Tuple[Locator, Optional[HealResult]]:
        try:
            # 1. Attempt standard find
            locator = self.page.locator(selector)
            locator.wait_for(state="attached", timeout=2000)
            return locator, None
            
        except Exception as e:
            logger.warning(f"⚠️ Locator FAILED: '{selector}'. Initiating AI Healing...")
            
            # 2. Capture Context for AI
            dom_snapshot = self.page.content()
            page_url = self.page.url
            
            # 3. Request Healing from MCP Server
            heal_result = api_client.request_healing(
                selector=selector,
                dom_snapshot=dom_snapshot,
                failure_reason=str(e),
                page_url=page_url,
                action=action,
                hints=hints,
                test_name="Universal_Ghost_Run"
            )
            
            if heal_result and heal_result.healed_locator:
                logger.info(f"✨ AI Found Healed Locator: {heal_result.healed_locator}")
                return self.page.locator(heal_result.healed_locator), heal_result
            
            # If AI fails, throw the original error
            raise e
