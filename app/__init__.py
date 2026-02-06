from flask import Flask
from flask_cors import CORS

from app.config import get_config


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for the Factor Analysis service.

    Args:
        config_name: Configuration environment (development/production/testing)
                    If None, reads from FLASK_ENV environment variable

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Enable CORS for Spring Boot backend and React frontend
    CORS(app, origins=config.CORS_ORIGINS)

    # Register blueprints
    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    return app
