import os
from groq import Groq
from supabase import create_client
from dotenv import load_dotenv

# Load env manually to be sure
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Checking Keys...")
print(f"GROQ_API_KEY: {GROQ_API_KEY[:10]}... (Length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0})")
print(f"SUPABASE_URL: {SUPABASE_URL}")

def test_groq():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY Missing")
        return

    client = Groq(api_key=GROQ_API_KEY)
    try:
        print("⏳ Testing Groq Connection...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "Tes 123"}],
            model="llama3-8b-8192",
        )
        print(f"✅ Groq Success! Response: {chat_completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Groq Failed: {e}")

def test_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase Keys Missing")
        return

    try:
        print("⏳ Testing Supabase Connection...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table('faq').select('*').limit(1).execute()
        print(f"✅ Supabase Success! Found {len(response.data)} rows.")
    except Exception as e:
        print(f"❌ Supabase Failed: {e}")

if __name__ == "__main__":
    test_groq()
    test_supabase()
