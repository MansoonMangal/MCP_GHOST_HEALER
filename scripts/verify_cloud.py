import httpx
import logging
import sys
from ghost_healer.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CloudVerify")


def verify_cloud_brain():
    url = settings.mcp_server.url
    logger.info(f"🔍 Testing connection to Cloud Brain: {url}")

    try:
        with httpx.Client(timeout=10.0) as client:

            # 1. Health Check
            response = client.get(f"{url}/health")

            if response.status_code == 200:
                logger.info(
                    f"✅ Cloud Brain is ONLINE (v{response.json().get('version')})"
                )
            else:
                logger.error(
                    f"❌ Cloud Brain returned status: {response.status_code}"
                )
                return False

            # 2. Mock Healing Test
            logger.info("🧠 Testing AI Matcher logic...")

            response = client.post(
                f"{url}/api/heal-locator",
                json={
                    "selector": "#login-button",
                    "action": "click",
                    "dom_snapshot": (
                        "<html><body>"
                        "<button id='new-login-v2'>Login</button>"
                        "</body></html>"
                    )
                }
            )

            if response.status_code == 200:
                data = response.json()

                logger.info(
                    f"✨ AI Healing Verified: "
                    f"Found '{data.get('healed_locator')}' "
                    f"with {data.get('confidence') * 100}% confidence."
                )

                return True

            else:
                logger.error(f"❌ AI Matcher failed: {response.text}")
                return False

    except Exception as e:
        logger.error(f"💥 Connectivity Error: {e}")

        logger.info(
            "TIP: If you are on Render's free tier, "
            "the server might be sleeping. Wait 30 seconds and retry."
        )

        return False


if __name__ == "__main__":
    success = verify_cloud_brain()
    sys.exit(0 if success else 1)