import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    PORT = int(os.getenv("PYTHON_SERVICE_PORT", 5000))
    DEBUG = False

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:8080,http://localhost:3000"
    ).split(",")

    # data paths
    FF_DATA_PATH = os.getenv(
        "FF_DATA_PATH",
        "data/F-F_Research_Data_5_Factors_2x3_daily.csv"
    )

    DEFAULT_LOOKBACK_YEARS = int(os.getenv("DEFAULT_LOOKBACK_YEARS", 3))

class DevelopmentConfig(Config):
    # Development configuration
    DEBUG = True

class ProductionConfig(Config):
    # Development configuration
    DEBUG = False

class TestingConfig(Config):
    # Development configuration
    DEBUG = True
    TESTING = True


# Config mapping
config_by_name = {
      "development": DevelopmentConfig,
      "production": ProductionConfig,
      "testing": TestingConfig
}

def get_config():
    # which configuration are we using
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)


