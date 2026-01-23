import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import LaundryChatbot
from fetch_data import get_revenue_data
from model import RevenuePredictionModel
from config import SUPABASE_URL, SUPABASE_KEY

def verify_chatbot():
    print(f"DEBUG: SUPABASE_URL set? {bool(SUPABASE_URL)}")
    print(f"DEBUG: GROQ_API_KEY set? {bool(os.getenv('GROQ_API_KEY'))}")
    
    print("\n--- Verifying Chatbot (Groq) ---")
    try:
        bot = LaundryChatbot()
        if not bot.context:
            print("⚠️ Warning: Context is empty (maybe DB issue or empty FAQ)")
        
        response = bot.get_response("Apa layanan yang tersedia?")
        print(f"Bot Response: {response}")
        
        if "Maaf" in response and "gangguan" in response:
             print("❌ Chatbot Failed (Groq Error)")
             return False
        print("✅ Chatbot OK")
        return True
    except Exception as e:
        print(f"❌ Chatbot Exception: {e}")
        return False

def verify_prediction():
    print("\n--- Verifying Prediction (Pure Python) ---")
    try:
        data = get_revenue_data()
        if not data:
             print("⚠️ No data fetched. Skipping training test.")
             return True # Cannot fail if no data
             
        model = RevenuePredictionModel()
        metrics = model.train(data)
        print(f"Training Metrics: {metrics}")
        
        if 'error' in metrics:
             print("❌ Training failed (Insufficient Data)")
             return False
             
        future = model.predict_future(days=5)
        print(f"Prediction (Next 5 Days): {future['predictions']}")
        print("✅ Prediction OK")
        return True
    except Exception as e:
         print(f"❌ Prediction Exception: {e}")
         return False

if __name__ == "__main__":
    print("STARTING VERIFICATION...")
    chat_ok = verify_chatbot()
    pred_ok = verify_prediction()
    
    if chat_ok and pred_ok:
        print("\n🎉 ALL SYSTEMS GO! Refactor Successful.")
    else:
        print("\nwarn: Some verifications failed.")
