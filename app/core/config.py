from app.services.config import load_config


def load_models_config():
    return load_config("app/core/files/models.yaml")