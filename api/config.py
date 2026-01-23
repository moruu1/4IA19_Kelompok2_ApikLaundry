import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key, default=None):
    # Try direct key
    val = os.getenv(key)
    if val: return val
    # Try VITE_ prefix
    val = os.getenv(f"VITE_{key}")
    if val: return val
    # Try NEXT_PUBLIC_ prefix
    val = os.getenv(f"NEXT_PUBLIC_{key}")
    if val: return val
    return default

SUPABASE_URL = get_env('SUPABASE_URL')
SUPABASE_KEY = get_env('SUPABASE_KEY') or get_env('SUPABASE_ANON_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
