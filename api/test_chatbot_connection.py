"""
Test script to verify chatbot database connection
This script will:
1. Check if environment variables are loaded
2. Test Supabase connection
3. Test if FAQ data can be retrieved
4. Test if chatbot can initialize and respond
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from groq import Groq

# Load environment variables
load_dotenv()

def print_separator():
    print("=" * 60)

def test_env_variables():
    """Test if environment variables are loaded"""
    print_separator()
    print("📋 STEP 1: Checking Environment Variables")
    print_separator()
    
    groq_key = os.getenv("GROQ_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    # Also check for alternative variable names
    supabase_url_alt = os.getenv("VITE_SUPABASE_URL")
    supabase_key_alt = os.getenv("VITE_SUPABASE_ANON_KEY")
    
    print(f"GROQ_API_KEY: {'✅ Found' if groq_key else '❌ Missing'}")
    if groq_key:
        print(f"  → Length: {len(groq_key)} characters")
        print(f"  → Preview: {groq_key[:15]}...")
    
    print(f"\nSUPABASE_URL: {'✅ Found' if supabase_url else '❌ Missing'}")
    if supabase_url:
        print(f"  → Value: {supabase_url}")
    
    print(f"SUPABASE_KEY: {'✅ Found' if supabase_key else '❌ Missing'}")
    if supabase_key:
        print(f"  → Length: {len(supabase_key)} characters")
        print(f"  → Preview: {supabase_key[:30]}...")
    
    # Check alternatives
    if not supabase_url and supabase_url_alt:
        print(f"\nVITE_SUPABASE_URL: ✅ Found as alternative")
        print(f"  → Value: {supabase_url_alt}")
        supabase_url = supabase_url_alt
    
    if not supabase_key and supabase_key_alt:
        print(f"VITE_SUPABASE_ANON_KEY: ✅ Found as alternative")
        print(f"  → Length: {len(supabase_key_alt)} characters")
        supabase_key = supabase_key_alt
    
    return groq_key, supabase_url, supabase_key

def test_supabase_connection(supabase_url, supabase_key):
    """Test Supabase connection and FAQ table"""
    print_separator()
    print("🔌 STEP 2: Testing Supabase Connection")
    print_separator()
    
    if not supabase_url or not supabase_key:
        print("❌ Cannot test Supabase - credentials missing!")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Try to fetch FAQ data
        print("\n🔍 Fetching data from 'faq' table...")
        response = supabase.table('faq').select('*').execute()
        data = response.data
        
        if data:
            print(f"✅ Successfully retrieved {len(data)} FAQ items!")
            print("\n📊 Sample FAQ data:")
            for i, item in enumerate(data[:3], 1):  # Show first 3 items
                print(f"\n  FAQ #{i}:")
                print(f"    Pertanyaan: {item.get('pertanyaan', 'N/A')[:60]}...")
                print(f"    Jawaban: {item.get('jawaban', 'N/A')[:60]}...")
            
            if len(data) > 3:
                print(f"\n  ... and {len(data) - 3} more FAQ items")
            
            return True
        else:
            print("⚠️ FAQ table is empty!")
            print("   → Chatbot won't have any knowledge to answer questions")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection FAILED!")
        print(f"   Error: {str(e)}")
        return False

def test_groq_connection(groq_key):
    """Test Groq AI connection"""
    print_separator()
    print("🤖 STEP 3: Testing Groq AI Connection")
    print_separator()
    
    if not groq_key:
        print("❌ Cannot test Groq - API key missing!")
        return False
    
    try:
        client = Groq(api_key=groq_key)
        print("✅ Groq client created successfully")
        
        print("\n🔍 Sending test message...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
            model="llama3-8b-8192",
            max_tokens=10
        )
        
        response = chat_completion.choices[0].message.content
        print(f"✅ Groq AI responded: '{response}'")
        return True
        
    except Exception as e:
        print(f"❌ Groq connection FAILED!")
        print(f"   Error: {str(e)}")
        return False

def test_chatbot_initialization():
    """Test if chatbot can initialize and respond"""
    print_separator()
    print("🎯 STEP 4: Testing Chatbot Initialization")
    print_separator()
    
    try:
        # Import chatbot class
        from chatbot import LaundryChatbot
        
        print("📦 Creating chatbot instance...")
        bot = LaundryChatbot()
        print("✅ Chatbot instance created!")
        
        # Check if context was loaded
        if bot.context and len(bot.context) > 100:
            print(f"✅ Knowledge base loaded ({len(bot.context)} characters)")
            print(f"\n📝 Context preview:\n{bot.context[:200]}...\n")
        else:
            print("⚠️ Knowledge base seems empty or not loaded properly")
            print(f"   Context length: {len(bot.context)} characters")
        
        # Test a real question
        print("\n🧪 Testing chatbot response...")
        test_question = "Halo, ini laundry apa?"
        print(f"   Question: '{test_question}'")
        
        response = bot.get_response(test_question)
        print(f"\n✅ Chatbot Response:\n{response}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Chatbot initialization FAILED!")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("🔍 CHATBOT DATABASE CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Step 1: Check environment variables
    groq_key, supabase_url, supabase_key = test_env_variables()
    
    # Step 2: Test Supabase connection
    supabase_ok = test_supabase_connection(supabase_url, supabase_key)
    
    # Step 3: Test Groq connection
    groq_ok = test_groq_connection(groq_key)
    
    # Step 4: Test chatbot initialization (only if all previous tests passed)
    chatbot_ok = False
    if supabase_ok and groq_ok:
        chatbot_ok = test_chatbot_initialization()
    else:
        print_separator()
        print("⏭️  STEP 4: SKIPPED (previous tests failed)")
        print_separator()
    
    # Final summary
    print_separator()
    print("📊 FINAL SUMMARY")
    print_separator()
    print(f"Environment Variables: {'✅ OK' if (groq_key and supabase_url and supabase_key) else '❌ MISSING'}")
    print(f"Supabase Connection:   {'✅ OK' if supabase_ok else '❌ FAILED'}")
    print(f"Groq AI Connection:    {'✅ OK' if groq_ok else '❌ FAILED'}")
    print(f"Chatbot Functionality: {'✅ OK' if chatbot_ok else '❌ FAILED'}")
    print_separator()
    
    if chatbot_ok:
        print("\n🎉 SUCCESS! Chatbot is properly connected to database!")
        print("   → Can retrieve FAQ data from Supabase")
        print("   → Can communicate with Groq AI")
        print("   → Ready to answer questions about Apik Laundry")
    else:
        print("\n⚠️  WARNING! Chatbot has connection issues!")
        if not supabase_ok:
            print("   → Fix Supabase credentials in .env file")
        if not groq_ok:
            print("   → Fix Groq API key in .env file")
        print("\n💡 TIP: Make sure your .env file contains:")
        print("   SUPABASE_URL=your_supabase_url")
        print("   SUPABASE_KEY=your_supabase_key")
        print("   GROQ_API_KEY=your_groq_key")
    
    print()

if __name__ == "__main__":
    main()
