"""
Configuration management for AI Resume Tailor
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-pro'

# Database Configuration
DATABASE_PATH = 'data/resume_context.db'

# File Processing Configuration
MAX_FILE_SIZE_MB = 10
SUPPORTED_FORMATS = ['.pdf', '.docx']
TEMP_DIR = 'data/temp'

# AI Processing Configuration
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Streamlit Configuration
PAGE_TITLE = "AI Resume Tailor"
PAGE_ICON = "📄"
LAYOUT = "wide"
