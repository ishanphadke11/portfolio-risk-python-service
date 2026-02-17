from flask import Flask
from flask_cors import CORS
from app.config import get_config
from app.routes.health import health_bp
from app.routes.analysis import analysis_bp

def create_app(config_name="development"):
    app = Flask(__name__)

    config = get_config()
    app.config.from_object(config)

    # enable CORS for spring boot backend
    CORS(app, origins=config.CORS_ORIGINS)

    app.register_blueprint(health_bp)
    app.register_blueprint(analysis_bp)

    return app
