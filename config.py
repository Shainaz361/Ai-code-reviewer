# --------- CONFIGURATION ---------
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

# Limits & Constraints
MAX_CODE_LENGTH = 50000  # 50KB
MIN_CODE_LENGTH = 2
MAX_TOKENS_ANALYSIS = 3000
MAX_TOKENS_CHAT = 1500
MAX_CHAT_HISTORY = 50
RATE_LIMIT_REQUESTS = 30
RATE_LIMIT_WINDOW = 60

# API Configuration
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env file!")
