import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv('PROJECT_NAME')
    API_VERSION: str = os.getenv('API_VERSION')
    API_VERSION_PREFIX: str = os.getenv('API_VERSION_PREFIX')
    ENVIRONMENT: str = os.getenv('ENVIRONMENT')
    CLASSIFIER_MODEL_PATH: str = os.getenv('CLASSIFIER_MODEL_PATH')
    EXPLAINER_MODEL_HF: str = os.getenv('EXPLAINER_MODEL_HF')

settings = Settings()
