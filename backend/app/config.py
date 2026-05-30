"""
VendorSentinel Configuration
Loads environment variables and provides typed settings.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Bright Data ──────────────────────────────────────────
    bright_data_api_token: str = ""
    
    # SERP API zone credentials
    bright_data_serp_username: str = ""
    bright_data_serp_password: str = ""
    
    # Web Unlocker zone credentials
    bright_data_unlocker_username: str = ""
    bright_data_unlocker_password: str = ""
    
    # Scraping Browser
    bright_data_browser_auth: str = ""
    bright_data_browser_host: str = "brd.superproxy.io:9515"
    
    # Web Scraper API
    bright_data_scraper_token: str = ""

    # ── AI/ML API ────────────────────────────────────────────
    aiml_api_key: str = ""
    aiml_api_base_url: str = "https://api.aimlapi.com/v1"

    # ── App Settings ─────────────────────────────────────────
    scan_interval_hours: int = 6
    alert_threshold_score: float = 7.0
    database_url: str = "sqlite:///./vendorsentinel.db"
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
