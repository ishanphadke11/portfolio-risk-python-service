from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for container orchestration and monitoring.

    Returns:
        JSON response with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "factor-analysis"
    }), 200
