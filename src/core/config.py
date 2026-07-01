"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Talent and Agent Orchestration Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "info"
    
    # Database
    database_url: str = "postgresql://talent_platform:talent_password@localhost:5432/talent_platform"
    test_database_url: str = "postgresql://talent_platform:talent_password@localhost:5432/talent_platform_test"
    
    # Authentication
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # OIDC
    oidc_issuer: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_redirect_uri: Optional[str] = None
    
    # Governance
    nvedo_email: Optional[str] = None
    data_governance_email: Optional[str] = None
    hr_business_partner_email: Optional[str] = None
    
    # Rate Limiting
    rate_limit_per_hour: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
