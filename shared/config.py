"""
Central configuration management with pydantic v1/v2 compatibility
"""
import os
from typing import Optional

# Handle both pydantic v1 and v2
try:
    from pydantic_settings import BaseSettings as PydanticBaseSettings
    PYDANTIC_V2 = True
except ImportError:
    try:
        from pydantic import BaseSettings as PydanticBaseSettings
        PYDANTIC_V2 = False
    except ImportError:
        raise ImportError(
            "Neither pydantic-settings nor pydantic BaseSettings found. "
            "Install with: pip install pydantic-settings"
        )

class Settings(PydanticBaseSettings):
    """Application settings with environment variable support"""
    
    # Server configurations
    QUERY_SERVER_URL: str = "http://localhost:8001"
    TRANSACTIONAL_SERVER_URL: str = "http://localhost:8002"
    EXTERNAL_API_SERVER_URL: str = "http://localhost:8003"
    
    # Agent Host configuration
    AGENT_HOST_PORT: int = 8000
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TIMEOUT: int = 30
    
    # MCP Client configuration
    MCP_CLIENT_TIMEOUT: int = 30
    MCP_CLIENT_MAX_RETRIES: int = 3
    MCP_CLIENT_RETRY_DELAY: float = 1.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "console"  # json or console

    # Madad Platform API
    MADAD_API_BASE_URL: Optional[str] = None
    MADAD_API_TIMEOUT: int = 30
    MADAD_MCP_AGENT_SECRET: Optional[str] = None

    # WhatsApp Cloud API
    WHATSAPP_GRAPH_API_BASE_URL: str = "https://graph.facebook.com"
    WHATSAPP_GRAPH_API_VERSION: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_API_TIMEOUT: int = 30
    
    # Health check
    HEALTH_CHECK_INTERVAL: int = 60
    
    if PYDANTIC_V2:
        model_config = {
            "env_file": ".env",
            "case_sensitive": True,
            "extra": "ignore"
        }
    else:
        class Config:
            env_file = ".env"
            case_sensitive = True

# Create singleton instance
try:
    settings = Settings()
except Exception as e:
    # Fallback to defaults if .env fails
    print(f"Warning: Failed to load settings from .env: {e}")
    print("Using default settings...")
    settings = Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        LOG_FORMAT=os.getenv("LOG_FORMAT", "console")
    )
