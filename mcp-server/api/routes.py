"""
Flask route definitions for the MCP Self-Healing Server.

Endpoints:
  POST /api/heal-locator        - Main healing pipeline entry point
  GET  /api/healing-history     - All historical healing records
  GET  /api/confidence-report   - Aggregated analytics
  GET  /api/execution-trace     - Full decision trace for a healing_id
  GET  /api/health              - Health check
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from services.healing_service import heal
from utils.db_manager import (
    get_all_healing_records,
    get_confidence_report_data,
    get_healing_record_by_id,
)
from utils.logger import get_logger
from config.settings import settings
from utils.stack_parser import stack_parser
from utils.universal_healer import source_healer

logger = get_logger("routes", settings.log_file, settings.log_level)
routes_bp = Blueprint('routes', __name__)

@routes_bp.route("/heal-locator", methods=["POST"])
def heal_locator():
    """
    Main healing endpoint.
    """
    data = request.json
    logger.info(f"POST /heal-locator | test={data.get('test_name')} | locator={data.get('original_locator')}")
    try:
        result = heal(
            original_locator=data.get('original_locator'),
            dom_snapshot=data.get('dom_snapshot'),
            failure_reason=data.get('failure_reason'),
            page_url=data.get('page_url'),
            action=data.get('action', 'click'),
            test_name=data.get('test_name'),
            element_hints=data.get('element_hints'),
        )
        
        # 🛡️ AUTOMATIC SOURCE HEALING (GHOST MODE)
        stack_trace = data.get('stack_trace')
        if stack_trace and result.get('decision') == 'AUTO_HEAL':
            file_name, line_num = stack_parser.parse(stack_trace)
            if file_name and line_num:
                # If it's a Java file, we might need to find the absolute path
                # For this demo, we assume the file is in the workspace
                source_healer.apply_fix(
                    file_path=file_name,
                    line_number=line_num,
                    old_locator=data.get('original_locator'),
                    new_locator=result.get('healed_locator')
                )

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in heal_locator: {e}", exc_info=True)
        return jsonify({"detail": str(e)}), 500

@routes_bp.route("/healing-history", methods=["GET"])
def healing_history():
    """Return all healing records, newest first. Supports filtering."""
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
        
    decision = request.args.get("decision")
    test_name = request.args.get("test_name")

    records = get_all_healing_records()

    if decision:
        records = [r for r in records if r.get("decision") == decision.upper()]
    if test_name:
        records = [r for r in records if r.get("test_name") == test_name]

    records = records[:limit]
    return jsonify(records)

@routes_bp.route("/confidence-report", methods=["GET"])
def confidence_report():
    """Return aggregated confidence statistics and score distribution."""
    data = get_confidence_report_data()
    return jsonify(data)

@routes_bp.route("/execution-trace/<healing_id>", methods=["GET"])
def execution_trace(healing_id):
    """Return full decision trace for a specific healing event."""
    record = get_healing_record_by_id(healing_id)
    if not record:
        return jsonify({"detail": f"Healing record '{healing_id}' not found"}), 404

    trace = record.get("execution_trace") or {}
    return jsonify({
        "healing_id": healing_id,
        "test_name": record.get("test_name"),
        "original_locator": record.get("original_locator", ""),
        "healed_locator": record.get("healed_locator"),
        "decision": record.get("decision", "FAIL"),
        "confidence_score": record.get("confidence_score", 0.0),
        "score_breakdown": record.get("score_breakdown", {}),
        "candidates_evaluated": record.get("candidates_evaluated", 0),
        "all_candidates": trace.get("all_candidates", []),
        "dom_elements_analyzed": record.get("dom_elements_analyzed", 0),
        "timestamp": record.get("timestamp", datetime.utcnow().isoformat()),
        "page_url": record.get("page_url", ""),
        "failure_reason": record.get("failure_reason", ""),
    })

@routes_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "MCP Self-Healing Server", "version": "1.0.0"})
