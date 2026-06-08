import os
import json
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Jeevs CBB API"
    api_description: str = "College Basketball Analytics API"
    api_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002", "http://127.0.0.1:3002"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Data Configuration
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    
    # Pagination Defaults
    default_limit: int = 50
    max_limit: int = 100
    
    # Search Configuration
    max_search_length: int = 100
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Roboflow Configuration
    roboflow_api_key: str = ""
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.strip() == "":
                return ["http://localhost:3000", "http://127.0.0.1:3000"]
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not valid JSON, treat as comma-separated string
                return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()