from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    # simple health check endpoint
    return jsonify({
        "status": "healthy",
        "service": "factor-analysis"

    }), 200