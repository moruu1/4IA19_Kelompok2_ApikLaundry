import os
from dotenv import load_dotenv

load_dotenv()

print("=== CHECKING ENV VARIABLES ===")
print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')[:20] if os.getenv('GROQ_API_KEY') else 'MISSING'}...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL') or 'MISSING'}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20] if os.getenv('SUPABASE_KEY') else 'MISSING'}...")

# Check alternative names
print("\n=== CHECKING ALTERNATIVE NAMES ===")
print(f"VITE_SUPABASE_URL: {os.getenv('VITE_SUPABASE_URL') or 'MISSING'}")
print(f"VITE_SUPABASE_ANON_KEY: {os.getenv('VITE_SUPABASE_ANON_KEY')[:20] if os.getenv('VITE_SUPABASE_ANON_KEY') else 'MISSING'}...")

# Now test Supabase if available
supabase_url = os.getenv('SUPABASE_URL') or os.getenv('VITE_SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('VITE_SUPABASE_ANON_KEY')

if supabase_url and supabase_key:
    print("\n=== TESTING SUPABASE CONNECTION ===")
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        response = supabase.table('faq').select('*').execute()
        print(f"SUCCESS! Found {len(response.data)} FAQ items")
        if response.data:
            print(f"First FAQ: {response.data[0].get('pertanyaan', 'N/A')[:50]}...")
    except Exception as e:
        print(f"FAILED: {e}")
else:
    print("\n=== SUPABASE SKIPPED (credentials missing) ===")
