import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the crypto conference scraper"""
    
    # API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = "o3"  # Model with web search capabilities
    
    # Google Sheets Configuration
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    GOOGLE_SPREADSHEET_NAME = os.getenv('GOOGLE_SPREADSHEET_NAME', 'Crypto Conferences 2026')
    USE_GOOGLE_SHEETS = os.getenv('USE_GOOGLE_SHEETS', 'true').lower() == 'true'
    
    # File paths
    INPUT_CSV = "[Shared Pantera] Conferences 2025 - 2025.csv"
    OUTPUT_2025_CSV = "conferences_2025.csv"
    OUTPUT_2026_CSV = "conferences_2026.csv"
    
    # Scraping configuration
    SCRAPING_INTERVAL_HOURS = 12
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30
    
    # Fields to scrape
    FIELDS_TO_SCRAPE = [
        "Start Date",
        "End Date", 
        "Location",
        "Speaker",
        "Attendees",
        "Status"
    ]
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraper.log"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if not os.path.exists(cls.INPUT_CSV):
            raise FileNotFoundError(f"Input CSV file not found: {cls.INPUT_CSV}")
        
        return True 