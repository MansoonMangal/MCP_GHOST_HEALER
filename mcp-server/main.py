"""
MCP Self-Healing Server — Flask Application Entry Point.

Run with:
  flask run --host=0.0.0.0 --port=8000
"""
from flask import Flask
from flask_cors import CORS

from api.routes import routes_bp
from config.settings import settings
from utils.db_manager import _ensure_db_files
from utils.logger import get_logger

logger = get_logger("main", settings.log_file, settings.log_level)

app = Flask(__name__)

# ── CORS — allow React dashboard and Playwright client ────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Register routes ───────────────────────────────────────────────────────────
app.register_blueprint(routes_bp, url_prefix='/api')

_ensure_db_files()
logger.info(
    f"MCP Server started | "
    f"auto_heal_threshold={settings.auto_heal_threshold} | "
    f"manual_review_threshold={settings.manual_review_threshold}"
)

if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
