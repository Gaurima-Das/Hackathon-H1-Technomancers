import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Jira Configuration
    JIRA_SERVER = os.getenv("JIRA_SERVER", "https://wideorbit.atlassian.net")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/jira_data.db")
    
    # API Configuration
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "Jira Management Dashboard"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 8 days
    
    # Email Configuration (for alerts)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "devdatatestingparvesh@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "uvdmagajanyrilef")

settings = Settings() 