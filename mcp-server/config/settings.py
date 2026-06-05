import os
from typing import Dict, List


def _parse_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "*")
    if raw.strip() == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


class Settings:
    # ── Server ──────────────────────────────────────────────────────────
    host: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port: int = int(os.getenv("MCP_SERVER_PORT", 8000))
    debug: bool = os.getenv("MCP_DEBUG", "false").lower() == "true"

    # ── Security ────────────────────────────────────────────────────────
    api_key: str = os.getenv("GHOST_API_KEY", os.getenv("API_KEY", ""))
    # Built into published SDKs — install-only access without manual keys
    sdk_public_key: str = os.getenv(
        "GHOST_SDK_PUBLIC_KEY",
        "gh_sdk_public_8f4a2c9e1b7d3f6a0e5c8b2d4f7a1e9",
    )
    cors_origins: List[str] = _parse_cors_origins()
    max_request_bytes: int = int(os.getenv("MAX_REQUEST_BYTES", str(5 * 1024 * 1024)))

    # ── Confidence Thresholds ────────────────────────────────────────────
    auto_heal_threshold: float = float(os.getenv("AUTO_HEAL_THRESHOLD", 50.0))
    manual_review_threshold: float = float(os.getenv("MANUAL_REVIEW_THRESHOLD", 30.0))

    # ── Similarity Weights (must sum to 1.0) ────────────────────────────
    weight_text_similarity: float = float(os.getenv("WEIGHT_TEXT_SIMILARITY", 0.35))
    weight_attribute_similarity: float = float(os.getenv("WEIGHT_ATTRIBUTE_SIMILARITY", 0.10))
    weight_dom_structure: float = float(os.getenv("WEIGHT_DOM_STRUCTURE", 0.20))
    weight_semantic_role: float = float(os.getenv("WEIGHT_SEMANTIC_ROLE", 0.25))
    weight_visibility: float = float(os.getenv("WEIGHT_VISIBILITY", 0.10))

    # ── Logging ──────────────────────────────────────────────────────────
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    _project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    log_file: str = os.getenv("LOG_FILE", os.path.join(_project_root, "reports", "logs", "mcp_server.log"))

    # ── Database ─────────────────────────────────────────────────────────
    db_path: str = os.getenv("DB_PATH", "database")
    # Render Postgres uses DATABASE_URL; MongoDB Atlas uses MONGO_URI (mongodb+srv://)
    database_url: str = (
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("MONGO_URI", "").strip()
    )
    mongo_uri: str = database_url  # backward-compatible alias

    def get_weights(self) -> Dict[str, float]:
        return {
            "text_similarity": self.weight_text_similarity,
            "attribute_similarity": self.weight_attribute_similarity,
            "dom_structure": self.weight_dom_structure,
            "semantic_role": self.weight_semantic_role,
            "visibility": self.weight_visibility,
        }


settings = Settings()
