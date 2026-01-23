from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Menambahkan direktori saat ini ke path agar import berfungsi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import LaundryChatbot
from predict import train_and_predict

app = Flask(__name__)
# Enable CORS for all domains to allow frontend access
CORS(app)

# Initialize Chatbot global variable
chatbot = None

def get_chatbot():
    global chatbot
    if chatbot is None:
        try:
            chatbot = LaundryChatbot()
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            return None
    return chatbot

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "API is running correctly"})

@app.route('/api/chat', methods=['POST'])
def chat():
    bot = get_chatbot()
    if not bot:
        return jsonify({"error": "Chatbot failed to initialize"}), 500
    
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
        
    user_message = data['message']
    response = bot.get_response(user_message)
    return jsonify({"response": response})

@app.route('/api/predict', methods=['GET'])
def predict():
    try:
        # Get 'days' parameter from query string, default to 30
        days = int(request.args.get('days', 30))
        result = train_and_predict(days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Handler for Vercel Serverless Function
# Vercel looks for 'app' object in this file
if __name__ == '__main__':
    app.run(debug=True)
