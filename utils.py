# --------- UTILITIES ---------
import streamlit as st
from datetime import datetime, timedelta
import os
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

class RateLimiter:
    """Rate limiting to prevent API abuse"""
    def __init__(self, max_requests=RATE_LIMIT_REQUESTS, window_seconds=RATE_LIMIT_WINDOW):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def is_allowed(self):
        """Check if request is allowed"""
        now = datetime.now()
        self.requests = [r for r in self.requests 
                        if now - r < timedelta(seconds=self.window_seconds)]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
    
    def get_remaining(self):
        """Get remaining requests in window"""
        now = datetime.now()
        self.requests = [r for r in self.requests 
                        if now - r < timedelta(seconds=self.window_seconds)]
        return self.max_requests - len(self.requests)


def validate_code(code):
    """Validate code input"""
    from config import MAX_CODE_LENGTH, MIN_CODE_LENGTH
    
    if not code or not code.strip():
        return False, "❌ Please paste some code first!"
    
    if len(code.strip()) < MIN_CODE_LENGTH:
        return False, f"⚠️ Code too short. Minimum {MIN_CODE_LENGTH} characters"
    
    if len(code) > MAX_CODE_LENGTH:
        return False, f"❌ Code too large. Maximum {MAX_CODE_LENGTH:,} characters"
    
    return True, "✅ Code is valid"


def detect_language(code):
    """Detect programming language from code snippet"""
    code_lower = code.lower()
    
    # Simple language detection
    if 'import ' in code_lower or 'from ' in code_lower or 'print(' in code_lower:
        return 'python'
    elif 'function ' in code_lower or 'const ' in code_lower or 'let ' in code_lower:
        return 'javascript'
    elif 'public class' in code_lower or 'private ' in code_lower:
        return 'java'
    elif '#include' in code_lower or 'cout <<' in code_lower:
        return 'cpp'
    elif 'package ' in code_lower or 'func ' in code_lower:
        return 'go'
    else:
        return 'python'  # Default


def get_code_metrics(code):
    """Get code metrics"""
    lines = code.split('\n')
    non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    
    return {
        'total_lines': len(lines),
        'code_lines': len(non_empty_lines),
        'characters': len(code),
        'functions': code.count('def ') + code.count('function '),
    }
