import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Jira Configuration
    JIRA_SERVER = os.getenv("JIRA_SERVER", "https://wideorbit.atlassian.net")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "parvesh.thapa@wideorbit.com")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/jira_data.db")
    
    # API Configuration
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "Jira Management Dashboard"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "GNVjWD9OVebs2VIWnXij8IIzrqLOCFIJvICH4s6Sj0w")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 8 days
    
    # Email Configuration (for alerts)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "devdatatestingparvesh@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "uvdmagajanyrilef")

settings = Settings() 