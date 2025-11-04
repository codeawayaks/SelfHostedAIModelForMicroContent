from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Runpod.io Configuration
    runpod_api_key: Optional[str] = None
    runpod_phi2_endpoint_id: Optional[str] = None
    runpod_mistral_endpoint_id: Optional[str] = None
    # Optional: Override model names if needed (leave empty to use default or endpoint's model)
    runpod_phi2_model_name: Optional[str] = None
    runpod_mistral_model_name: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///./generations.db"
    
    # Application Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate_runpod_config(self):
        """Validate that Runpod configuration is set"""
        if not self.runpod_api_key:
            raise ValueError(
                "RUNPOD_API_KEY is required. Please set it in your .env file."
            )
        if not self.runpod_phi2_endpoint_id:
            raise ValueError(
                "RUNPOD_PHI2_ENDPOINT_ID is required. Please set it in your .env file. "
                "See RUNPOD_SETUP.md for instructions on deploying models."
            )
        if not self.runpod_mistral_endpoint_id:
            raise ValueError(
                "RUNPOD_MISTRAL_ENDPOINT_ID is required. Please set it in your .env file. "
                "See RUNPOD_SETUP.md for instructions on deploying models."
            )


settings = Settings()

# Validate Runpod config only when actually used (lazy validation)
def get_settings() -> Settings:
    """Get settings with validation"""
    settings.validate_runpod_config()
    return settings

