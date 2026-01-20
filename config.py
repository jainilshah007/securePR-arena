from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # AgentArena
    agentarena_api_key: str
    webhook_auth_token: str
    
    # SecurePR Production API
    securepr_api_url: str
    securepr_api_key: str
    
    # Optional
    temp_dir: str = "/tmp/arena_repos"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure temp directory exists
Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
