import os
from typing import Dict

class Settings:
    # ── Server ──────────────────────────────────────────────────────────
    host: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port: int = int(os.getenv("MCP_SERVER_PORT", 8000))
    debug: bool = os.getenv("MCP_DEBUG", "true").lower() == "true"

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
    
    # Dynamically resolve to workspace root to ensure it is always in reports/logs/mcp_server.log
    _project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    log_file: str = os.getenv("LOG_FILE", os.path.join(_project_root, "reports", "logs", "mcp_server.log"))

    # ── Database ─────────────────────────────────────────────────────────
    db_path: str = os.getenv("DB_PATH", "database")
    mongo_uri: str = os.getenv("MONGO_URI", "")          # Set by Render in production

    def get_weights(self) -> Dict[str, float]:
        return {
            "text_similarity": self.weight_text_similarity,
            "attribute_similarity": self.weight_attribute_similarity,
            "dom_structure": self.weight_dom_structure,
            "semantic_role": self.weight_semantic_role,
            "visibility": self.weight_visibility,
        }

settings = Settings()
