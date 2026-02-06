import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Service settings
    PORT = int(os.getenv("PYTHON_SERVICE_PORT", 5001))
    DEBUG = False

    # CORS - allowed origins (comma-separated in env var)
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8080,http://localhost:3000"
    ).split(",")

    # Data paths
    FF_DATA_PATH = os.getenv(
        "FF_DATA_PATH",
        "data/F-F_Research_Data_5_Factors_2x3_daily.csv"
    )

    # Default analysis date range (years)
    DEFAULT_LOOKBACK_YEARS = int(os.getenv("DEFAULT_LOOKBACK_YEARS", 3))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


# Config mapping
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
