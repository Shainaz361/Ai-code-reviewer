import streamlit as st
import json
import os
from groq import Groq
from datetime import datetime
import time
from dotenv import load_dotenv
from config import GROQ_API_KEY, MODEL, MAX_CODE_LENGTH, MAX_TOKENS_ANALYSIS, MAX_TOKENS_CHAT, RATE_LIMIT_WINDOW
from utils import RateLimiter, validate_code, detect_language, get_code_metrics

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# --------- RATE LIMITER ---------
if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter()

# --------- PAGE CONFIG ---------
st.set_page_config(
    page_title="AI Code Review Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------- CACHED GROQ CLIENT ---------
@st.cache_resource
def get_groq_client():
    """Get singleton Groq client"""
    try:
        return Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq: {str(e)}")
        st.stop()

# --------- CUSTOM CSS (ADVANCED) ---------
st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
        50% { box-shadow: 0 0 40px rgba(59, 130, 246, 0.5); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Premium Light SaaS - Advanced Gradient */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 20%, #e8f1ff 40%, #e0e7ff 50%, #f5f9ff 80%, #ffffff 100%);
        background-attachment: fixed;
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Main container */
    .main {
        background-color: transparent;
        animation: fadeIn 1s ease-out;
    }
    
    /* Sidebar background - Advanced glass morphism */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 250, 255, 0.8) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(191, 219, 254, 0.5);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
    }
    
    /* Professional typography with smooth rendering */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    body, p, span, div {
        color: #1e293b;
        letter-spacing: 0.3px;
        transition: color 0.3s ease;
    }
    
    /* Main title - Premium animated gradient */
    .main-title {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 25%, #1d4ed8 50%, #60a5fa 75%, #3b82f6 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 0.5rem;
        animation: fadeIn 1s ease-out;
        text-shadow: 0 2px 10px rgba(59, 130, 246, 0.15);
    }
    
    /* Subtitle */
    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
        line-height: 1.7;
        animation: slideInLeft 1.2s ease-out;
    }
    
    /* Advanced card design */
    .stAlert {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 250, 255, 0.85) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(191, 219, 254, 0.5);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12), 0 2px 4px rgba(0, 0, 0, 0.04);
        animation: fadeIn 0.6s ease-out;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stAlert:hover {
        box-shadow: 0 12px 48px rgba(59, 130, 246, 0.18), 0 4px 8px rgba(0, 0, 0, 0.06);
        border-color: rgba(59, 130, 246, 0.6);
        transform: translateY(-2px);
    }
    
    /* Info Box */
    .stInfo {
        background: linear-gradient(135deg, rgba(224, 242, 254, 0.7) 0%, rgba(240, 248, 255, 0.5) 100%);
        border: 1px solid rgba(147, 197, 253, 0.5);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
    }
    
    .stInfo:hover {
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12);
    }
    
    /* Success Box */
    .stSuccess {
        background: linear-gradient(135deg, rgba(220, 252, 231, 0.7) 0%, rgba(240, 253, 244, 0.5) 100%);
        border: 1px solid rgba(134, 239, 172, 0.5);
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Warning Box */
    .stWarning {
        background: linear-gradient(135deg, rgba(254, 243, 199, 0.7) 0%, rgba(254, 252, 232, 0.5) 100%);
        border: 1px solid rgba(250, 204, 21, 0.5);
    }
    
    /* Error Box */
    .stError {
        background: linear-gradient(135deg, rgba(254, 226, 226, 0.7) 0%, rgba(254, 242, 242, 0.5) 100%);
        border: 1px solid rgba(248, 113, 113, 0.5);
    }
    
    /* Advanced buttons with advanced effects */
    button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        letter-spacing: 0.6px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.35), 0 1px 3px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.6s ease;
    }
    
    button:hover::before {
        left: 100%;
    }
    
    button:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 40px rgba(59, 130, 246, 0.5), 0 4px 8px rgba(0, 0, 0, 0.12);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%);
    }
    
    button:active {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }
    
    /* Input fields - Advanced with animations */
    input, textarea {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.8) 100%);
        border: 1.5px solid rgba(191, 219, 254, 0.4);
        border-radius: 12px;
        color: #1e293b;
        padding: 0.85rem 1.1rem;
        font-size: 0.95rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 12px rgba(59, 130, 246, 0.08), inset 0 1px 2px rgba(0, 0, 0, 0.02);
        font-weight: 500;
    }
    
    input::placeholder, textarea::placeholder {
        color: #cbd5e1;
        font-weight: 400;
    }
    
    input:focus, textarea:focus {
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(230, 244, 255, 0.9) 100%);
        border-color: #60a5fa;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), 0 4px 20px rgba(59, 130, 246, 0.2);
        outline: none;
        transform: translateY(-2px);
    }
    
    /* Text areas - Advanced code styling */
    textarea {
        font-family: 'Fira Code', 'Menlo', 'Monaco', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        letter-spacing: 0.5px;
    }
    
    /* Divider - Advanced with glow effect */
    hr {
        border: none;
        height: 1.5px;
        background: linear-gradient(90deg, transparent, rgba(147, 197, 253, 0.4), rgba(59, 130, 246, 0.3), rgba(147, 197, 253, 0.4), transparent);
        margin: 2rem 0;
        box-shadow: 0 2px 12px rgba(59, 130, 246, 0.08);
    }
    
    /* Tabs - Advanced with animated underline */
    [data-baseweb="tab-list"] {
        border-bottom: 2px solid rgba(191, 219, 254, 0.3);
        transition: all 0.3s ease;
    }
    
    [role="tab"] {
        color: #64748b;
        font-weight: 700;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        padding-bottom: 12px;
    }
    
    [role="tab"]:hover {
        color: #3b82f6;
        box-shadow: inset 0 -2px 0 0 rgba(59, 130, 246, 0.2);
    }
    
    [role="tab"][aria-selected="true"] {
        color: #3b82f6;
        border-bottom: 3px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
    }
    
    /* Metrics - Advanced gradient */
    [data-testid="stMetricValue"] {
        color: #1e293b;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeIn 0.8s ease-out;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }
    
    /* Expanders - Advanced */
    [data-testid="stExpander"] {
        border: 1.5px solid rgba(191, 219, 254, 0.4);
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(240, 248, 255, 0.6) 100%);
        box-shadow: 0 2px 16px rgba(59, 130, 246, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.6s ease-out;
    }
    
    [data-testid="stExpander"]:hover {
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.6);
    }
    
    /* Code blocks - Advanced syntax styling */
    code {
        background: linear-gradient(135deg, rgba(219, 234, 254, 0.7) 0%, rgba(240, 248, 255, 0.5) 100%);
        color: #1e40af;
        border-radius: 8px;
        padding: 0.35rem 0.7rem;
        font-family: 'Fira Code', 'Menlo', monospace;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.12);
        transition: all 0.3s ease;
    }
    
    code:hover {
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
    }
    
    /* Pre blocks - Advanced with glow */
    pre {
        background: linear-gradient(135deg, rgba(240, 248, 255, 0.9) 0%, rgba(224, 242, 254, 0.7) 100%);
        border: 1.5px solid rgba(191, 219, 254, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        overflow-x: auto;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    pre:hover {
        box-shadow: 0 12px 48px rgba(59, 130, 246, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        border-color: rgba(59, 130, 246, 0.6);
    }
    
    /* Links - Advanced with underline animation */
    a {
        color: #3b82f6;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 600;
        position: relative;
        border-bottom: 2px solid transparent;
    }
    
    a:hover {
        color: #2563eb;
        border-bottom-color: #2563eb;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(240, 250, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #3b82f6, #60a5fa);
        border-radius: 10px;
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #2563eb, #3b82f6);
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }
    
    /* Advanced badge styling */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        animation: fadeIn 0.6s ease-out;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-success {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(134, 239, 172, 0.15));
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #15803d;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(251, 191, 36, 0.15));
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #d97706;
    }
    
    .badge-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(252, 165, 165, 0.15));
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #991b1b;
    }
    
    .badge-info {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 197, 253, 0.15));
        border: 1px solid rgba(59, 130, 246, 0.4);
        color: #1e40af;
    }
    
    /* Stats card styling */
    .stats-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.85) 100%);
        border: 1.5px solid rgba(191, 219, 254, 0.4);
        border-radius: 14px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.18);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* Code metrics display */
    .code-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Scrollable code boxes */
    .code-box {
        background: linear-gradient(135deg, rgba(240, 248, 255, 0.9) 0%, rgba(224, 242, 254, 0.7) 100%);
        border: 1.5px solid rgba(191, 219, 254, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        overflow-y: auto;
        max-height: 600px;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .code-box:hover {
        box-shadow: 0 12px 48px rgba(59, 130, 246, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        border-color: rgba(59, 130, 246, 0.6);
    }
    
    .code-box-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input textarea styling for code boxes */
    .code-input-area {
        width: 100%;
        height: 500px;
        font-family: 'Fira Code', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        padding: 1rem;
        border: 1px solid rgba(191, 219, 254, 0.3);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.95);
        color: #1e293b;
        resize: vertical;
    }
    
    .code-input-area:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }
    
    .code-stat-item {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(147, 197, 253, 0.08));
        border-left: 3px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .code-stat-item:hover {
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        border-left-color: #2563eb;
    }
    
    .code-stat-value {
        font-size: 1.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .code-stat-label {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 700;
        margin-top: 0.5rem;
        letter-spacing: 0.5px;
    }
    
    /* Language badge */
    .language-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
        animation: slideInLeft 0.6s ease-out;
    }
    
    /* Advanced section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(191, 219, 254, 0.3);
    }
    
    .section-header-icon {
        font-size: 1.8rem;
        animation: fadeIn 0.8s ease-out;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e293b, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Advanced chat message styling */
    .chat-message {
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        animation: slideInLeft 0.4s ease-out;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(147, 197, 253, 0.08));
        border-left-color: #2563eb;
        margin-left: 2rem;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(134, 239, 172, 0.08));
        border-left-color: #16a34a;
        margin-right: 2rem;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-success {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(134, 239, 172, 0.15));
        color: #16a34a;
    }
    
    .status-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(251, 191, 36, 0.15));
        color: #ca8a04;
    }
    
    .status-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(252, 165, 165, 0.15));
        color: #dc2626;
    }
    
    /* Animated dot */
    @keyframes dot {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }
    
    .animated-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3b82f6;
        animation: dot 1.5s infinite;
    }
    </style>
""", unsafe_allow_html=True)

# --------- MAIN HEADER ---------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<h1 class="main-title">🔍 AI Code Review Agent</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">✨ Intelligent code analysis powered by Groq AI - Get detailed insights on bugs, security, and improvements</p>',
        unsafe_allow_html=True
    )

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/4076/4076438.png", width=100)

st.divider()

# --------- SIDEBAR CONFIGURATION ---------
with st.sidebar:
    st.divider()
    
    # Statistics - Load reviews safely
    st.markdown("### 📊 Statistics")
    try:
        with open("reviews.json", "r") as f:
            reviews_data = json.load(f)
        total_reviews = len(reviews_data) if isinstance(reviews_data, list) else 0
    except (FileNotFoundError, json.JSONDecodeError):
        total_reviews = 0
    
    st.metric("📋 Total Reviews", total_reviews)
    
    st.divider()
    
    # Features
    st.markdown("### 🎯 Features")
    st.write("✅ AI-powered code analysis")
    st.write("🔒 Security vulnerability detection")
    st.write("🐛 Bug identification")
    st.write("⚡ Performance optimization tips")
    st.write("💾 Review history tracking")
    st.write("📥 Export reviews")
    
    st.divider()
    
    st.markdown("### 📚 Supported Languages")
    st.write("• Python • JavaScript • Java • C/C++ • Go • Rust • PHP • Ruby")

# --------- AI ANALYZER FUNCTION -----------
def analyze_code_with_ai(code):
    """Use Groq API to analyze code with input validation"""
    # Validate input
    is_valid, message = validate_code(code)
    if not is_valid:
        return None, message
    
    # Check rate limit
    if not st.session_state.rate_limiter.is_allowed():
        remaining = st.session_state.rate_limiter.get_remaining()
        return None, f"⏱️ Rate limited. Please wait before analyzing more code. Resets in {RATE_LIMIT_WINDOW}s"
    
    try:
        client = get_groq_client()
        
        prompt = f"""You are a code reviewer. Analyze the code briefly and provide:

1. **Issues Found** (be SPECIFIC):
   - Syntax errors (missing parentheses, missing closing tags, unclosed strings, etc.)
   - Logic errors
   - Missing imports
   - DETAIL WHAT IS MISSING AND WHERE
   
   Example format:
   - Line 1: Missing () after st.divider
   - Line 3: Missing closing </span> tag
   - Line 4: Missing closing </div> tag
   - Line 5: Missing closing triple quotes

2. **What Was Missing/Fixed** (brief list of fixes made)

3. **COMPLETE IMPROVED CODE** - Full working code with:
   - ALL missing parentheses () added
   - ALL missing closing tags (</div>, </span>, etc.) added
   - ALL missing closing quotes added
   - ALL syntax errors fixed
   - Ready to run

Be VERY SPECIFIC about what was missing in the Issues Found section.

Code to review:
```
{code}
```"""

        message = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_ANALYSIS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        analysis = message.choices[0].message.content
        return analysis, None
    
    except TimeoutError:
        return None, "⏱️ API timeout - please try again"
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# --------- SAVE REVIEW FUNCTION -----------
def save_review(code, analysis, source="AI"):
    """Save code review to JSON file with error handling"""
    if not code or not analysis:
        return False
    
    data = {
        "code": code,
        "analysis": analysis,
        "source": source,
        "timestamp": str(datetime.now())
    }

    try:
        with open("reviews.json", "r") as f:
            reviews = json.load(f)
            if not isinstance(reviews, list):
                reviews = []
    except (FileNotFoundError, json.JSONDecodeError):
        reviews = []

    reviews.append(data)

    try:
        with open("reviews.json", "w") as f:
            json.dump(reviews, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Failed to save review: {str(e)}")
        return False


# --------- LOAD REVIEWS FUNCTION -----------
def load_reviews():
    """Load reviews from JSON file with error handling"""
    try:
        with open("reviews.json", "r") as f:
            reviews = json.load(f)
            return reviews if isinstance(reviews, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# --------- CHATBOT FUNCTION -----------
def chat_with_ai(user_message, conversation_history):
    """Chat with AI - answer any user questions"""
    # Check rate limit
    if not st.session_state.rate_limiter.is_allowed():
        return None, f"⏱️ Rate limited. Please wait before sending more messages."
    
    try:
        client = get_groq_client()
        
        # Build messages list with history (limit to recent messages)
        messages = []
        for msg in conversation_history[-10:]:  # Keep last 10 messages
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_CHAT,
            messages=messages
        )
        
        assistant_message = response.choices[0].message.content
        return assistant_message, None
    
    except TimeoutError:
        return None, "⏱️ API timeout - please try again"
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# --------- MAIN TABS ---------
tab1, tab2, tab3 = st.tabs(["🚀 Analyze Code", "📂 Review History", "💬 Chat Assistant"])

# --------- TAB 1: ANALYZE CODE ---------
with tab1:
    st.markdown('<div class="section-header"><span class="section-header-icon">📝</span><span class="section-title">Code Analysis</span></div>', unsafe_allow_html=True)
    
    # Initialize analysis state
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "analysis_error" not in st.session_state:
        st.session_state.analysis_error = None
    if "current_code" not in st.session_state:
        st.session_state.current_code = ""
    if "improved_code" not in st.session_state:
        st.session_state.improved_code = ""
    
    # Quick tips info box
    st.markdown("### 💡 How to Use")
    col_tips, col_blank = st.columns([2, 1])
    with col_tips:
        st.info(
            """
            1. **Paste your code** in the left box below
            2. **Click Analyze** to get AI review
            3. **View improved code** on the right
            4. **Copy & use** the corrected code
            """
        )
    
    st.divider()
    
    # Action Buttons (Top)
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([2, 2, 1, 1])
    
    with col_btn1:
        analyze_clicked = st.button(
            "🚀 Analyze Code",
            use_container_width=True,
            type="primary"
        )
    
    with col_btn2:
        clear_clicked = st.button(
            "🗑️ Clear All",
            use_container_width=True
        )
    
    with col_btn3:
        copy_input = st.button(
            "📋 Copy Input",
            use_container_width=True,
            help="Copy input code to clipboard"
        )
    
    with col_btn4:
        copy_output = st.button(
            "📋 Copy Output",
            use_container_width=True,
            help="Copy improved code"
        )
    
    if clear_clicked:
        st.session_state.analysis_result = None
        st.session_state.analysis_error = None
        st.session_state.current_code = ""
        st.session_state.improved_code = ""
        st.rerun()
    
    st.divider()
    
    # MAIN SECTION: TWO BOXES SIDE-BY-SIDE
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    # ===== LEFT COLUMN: INPUT CODE BOX =====
    with col_left:
        st.markdown("### 📥 Input Code")
        
        # Text area for code input
        code_input = st.text_area(
            "Paste your code here:",
            height=340,
            placeholder="Paste Python, JavaScript, Java, C++, or any code...",
            label_visibility="collapsed",
            key="code_input_area"
        )
        
        # Show code metrics
        if code_input.strip():
            st.divider()
            metrics = get_code_metrics(code_input)
            lang = detect_language(code_input)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                st.metric("Lines", metrics["total_lines"])
            with col_m2:
                st.metric("Chars", len(code_input))
            with col_m3:
                st.markdown(f"<div class='language-badge'>{lang.upper()}</div>", unsafe_allow_html=True)
    
    # ===== RIGHT COLUMN: OUTPUT BOX =====
    with col_right:
        st.markdown("### ✨ Review Output")
        
        # Analysis Logic - Execute when button clicked
        if analyze_clicked:
            is_valid, validation_msg = validate_code(code_input)
            
            if not is_valid:
                st.session_state.analysis_error = validation_msg
                st.session_state.analysis_result = None
            else:
                # Show progress with loading indicator
                with st.status("🔍 Analyzing your code...", expanded=True) as status:
                    status.write("📋 Validating code...")
                    time.sleep(0.3)
                    
                    status.write("🤖 Analyzing with AI...")
                    analysis, error = analyze_code_with_ai(code_input)
                    
                    if not error:
                        status.write("💾 Saving review...")
                        time.sleep(0.2)
                        save_review(code_input, analysis, source="Groq AI")
                        st.session_state.analysis_result = analysis
                        st.session_state.analysis_error = None
                        st.session_state.current_code = code_input
                        status.update(label="✅ Analysis Complete!", state="complete")
                    else:
                        st.session_state.analysis_error = error
                        st.session_state.analysis_result = None
                        status.update(label="❌ Analysis Failed", state="error")
        
        # Display Results in Right Box
        if st.session_state.analysis_error:
            st.error(f"⚠️ {st.session_state.analysis_error}")
        elif st.session_state.analysis_result:
            analysis_text = st.session_state.analysis_result
            
            if "COMPLETE IMPROVED CODE" in analysis_text:
                parts = analysis_text.split("COMPLETE IMPROVED CODE")
                improved = parts[-1].strip() if len(parts) > 1 else analysis_text
                improved = improved.replace("```", "").strip()
            else:
                improved = analysis_text
            
            st.session_state.improved_code = improved
            
            output_cols = st.columns([1, 1], gap="medium")
            
            with output_cols[0]:
                st.markdown("#### ✨ Improved Code")
                st.text_area(
                    "Improved code",
                    value=improved,
                    height=320,
                    label_visibility="collapsed",
                    disabled=True
                )
                st.download_button(
                    label="📥 Download Improved Code",
                    data=improved,
                    file_name=f"improved_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with output_cols[1]:
                st.markdown("#### 🔍 Analysis Summary")
                st.text_area(
                    "Full analysis",
                    value=analysis_text,
                    height=320,
                    label_visibility="collapsed",
                    disabled=True
                )
        else:
            st.info("👈 Paste code on the left and click 'Analyze' to see improved code here")
    
    st.divider()
    
    # CHAT SECTION BELOW
    st.markdown('<div class="section-header"><span class="section-header-icon">💬</span><span class="section-title">Chat Assistant</span></div>', unsafe_allow_html=True)
    st.markdown("Ask follow-up questions about your code analysis!")
    
    # Initialize chat history in session state
    if "chat_history_tab1" not in st.session_state:
        st.session_state.chat_history_tab1 = []
    
    # Display chat history in a compact format
    if st.session_state.chat_history_tab1:
        st.markdown(f'<span class="badge badge-info">💬 {len(st.session_state.chat_history_tab1)//2} Messages</span>', unsafe_allow_html=True)
        
        chat_container = st.container()
        with chat_container:
            for idx, msg in enumerate(st.session_state.chat_history_tab1[-6:]):  # Show last 6 messages
                if msg["role"] == "user":
                    st.html(f'<div class="chat-message user"><strong>🙋 You:</strong> {msg["content"]}</div>')
                else:
                    st.html(f'<div class="chat-message assistant"><strong>🤖 Assistant:</strong> {msg["content"]}</div>')
    
    # User input section
    col_chat_input, col_chat_send, col_chat_clear = st.columns([4, 1, 1])
    
    with col_chat_input:
        user_question = st.text_input(
            "Message:",
            placeholder="Ask about the analysis or anything else...",
            label_visibility="collapsed",
            key="chat_input_tab1"
        )
    
    with col_chat_send:
        send_button = st.button("📤", use_container_width=True, type="primary", help="Send message", key="send_btn_tab1")
    
    with col_chat_clear:
        if st.button("🗑️", use_container_width=True, help="Clear chat", key="clear_btn_tab1"):
            st.session_state.chat_history_tab1 = []
            st.rerun()
    
    # Handle chat logic
    if send_button and user_question.strip():
        # Add user message to history
        st.session_state.chat_history_tab1.append({
            "role": "user",
            "content": user_question
        })
        
        # Show thinking animation
        with st.spinner("🤖 Thinking..."):
            response, error = chat_with_ai(user_question, st.session_state.chat_history_tab1)
        
        if error:
            st.error(error)
        else:
            # Add assistant response to history
            st.session_state.chat_history_tab1.append({
                "role": "assistant",
                "content": response
            })
            
            # Rerun to display updated chat
            st.rerun()



# --------- TAB 2: REVIEW HISTORY ---------
with tab2:
    st.markdown("### 📜 Past Code Reviews")
    
    reviews = load_reviews()
    
    if reviews:
        st.info(f"📊 Total reviews archived: **{len(reviews)}**")
        st.divider()
        
        # Display reviews in reverse order (newest first)
        for idx in range(len(reviews) - 1, -1, -1):
            review_num = len(reviews) - idx
            review = reviews[idx]
            
            # Safety check for review structure
            if not isinstance(review, dict) or "analysis" not in review or "code" not in review:
                continue
            
            # Create expander for each review
            with st.expander(
                f"📋 Review #{review_num} • {review.get('timestamp', 'Unknown')}",
                expanded=False
            ):
                col_content, col_actions = st.columns([4, 1])
                
                with col_content:
                    # Display Code
                    st.markdown("#### 📋 Code:")
                    st.code(review["code"], language="python")
                    
                    st.divider()
                    
                    # Display Analysis
                    st.markdown("#### 🔍 Analysis:")
                    st.markdown(review["analysis"])
                
                with col_actions:
                    # Delete button
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{idx}",
                        use_container_width=True
                    ):
                        reviews.pop(idx)
                        try:
                            with open("reviews.json", "w") as f:
                                json.dump(reviews, f, indent=4)
                            st.success("✅ Review deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete review: {str(e)}")
            
            st.divider()
        
        # Clear all reviews button
        col_clear1, col_clear2 = st.columns([1, 1])
        with col_clear1:
            if st.button("🗑️ Clear All Reviews", use_container_width=True):
                st.warning("⚠️ This will delete all reviews. Are you sure?")
                if st.button("✅ Yes, Delete All", use_container_width=True):
                    try:
                        with open("reviews.json", "w") as f:
                            json.dump([], f)
                        st.success("✅ All reviews cleared!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to clear reviews: {str(e)}")
    
    else:
        st.info("📭 No reviews yet. Submit code in the 'Analyze Code' tab to get started!")


# --------- TAB 3: CHAT ASSISTANT ---------
with tab3:
    st.markdown('<div class="section-header"><span class="section-header-icon">💬</span><span class="section-title">Chat Assistant</span></div>', unsafe_allow_html=True)
    st.markdown("Ask me anything! I can help with code, questions, explanations, and more.")
    
    st.divider()
    
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown(f'<span class="badge badge-info">💬 {len(st.session_state.chat_history)//2} Messages</span>', unsafe_allow_html=True)
        st.divider()
        
        # Create a scrollable chat container
        chat_col = st.columns(1)[0]
        with chat_col:
            for idx, msg in enumerate(st.session_state.chat_history):
                if msg["role"] == "user":
                    st.html(f'<div class="chat-message user"><strong>🙋 You:</strong> {msg["content"]}</div>')
                else:
                    st.html(f'<div class="chat-message assistant"><strong>🤖 Assistant:</strong> {msg["content"]}</div>')
    else:
        st.info("💭 Start a conversation by asking a question!")
    
    st.divider()
    
    # User input section
    st.markdown("### ✍️ Your Question")
    
    col_input, col_send = st.columns([5, 1])
    
    with col_input:
        user_question = st.text_input(
            "Message:",
            placeholder="Ask me anything about code, programming, or anything else...",
            label_visibility="collapsed"
        )
    
    with col_send:
        send_button = st.button("📤", use_container_width=True, type="primary", help="Send message")
    
    # Handle chat logic
    if send_button and user_question.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Show thinking animation
        with st.spinner("🤖 Thinking..."):
            response, error = chat_with_ai(user_question, st.session_state.chat_history)
        
        if error:
            st.error(error)
        else:
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Rerun to display updated chat
            st.rerun()
    
    # Chat controls
    st.divider()
    
    col_clear, col_count = st.columns([1, 1])
    
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ Chat history cleared!")
            st.rerun()
    
    with col_count:
        if st.session_state.chat_history:
            st.html(f'<div class="status-indicator status-success">✅ {len(st.session_state.chat_history)//2} exchanges</div>')

# --------- FOOTER ---------
st.divider()

footer_cols = st.columns([1, 1, 1, 1])

with footer_cols[0]:
    st.markdown("#### 🚀 Powered by")
    st.write("**Groq AI**")

with footer_cols[1]:
    st.markdown("#### ℹ️ About")
    st.write("Code Review Agent")

with footer_cols[2]:
    pass

with footer_cols[3]:
    pass

st.markdown("---")
st.caption("🔒 Secure • ⚡ Fast • 🧠 Intelligent Code Review")