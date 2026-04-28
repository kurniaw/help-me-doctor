from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "helpmedoctor"

    # JWT
    jwt_secret: str = "77e89f7507d436c95abe888f397bc7ba367e68dbd011f99de263da50f626bd39"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 90

    # GCP / Vertex AI
    gcp_project_id: str = "ntu-data-science-ai"
    gcp_region: str = "asia-southeast1"       # used for Matching Engine index
    gemini_region: str = "us-central1"        # Gemini models are available here
    vertex_index_id: str = ""
    vertex_index_endpoint_id: str = ""
    vertex_deployed_index_id: str = "hmd_medical_deployed"

    # Google credentials
    google_application_credentials: str = ""
    google_api_key: str = ""

    # Data directory
    data_dir: str = "../data"

    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-004"


@lru_cache
def get_settings() -> Settings:
    return Settings()
