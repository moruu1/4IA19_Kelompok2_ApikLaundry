from flask import Flask, jsonify, request
from flask_cors import CORS
from model import RevenuePredictionModel
from fetch_data import get_revenue_data
from chatbot import LaundryChatbot
from datetime import datetime
from inventory import InventoryPredictor
import os

app = Flask(__name__)
# Enable CORS for all origins (needed for ngrok)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Cache model in memory with timestamp
model_cache = {
    'model': None,
    'trained_at': None,
    'data_size': 0
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Revenue prediction API is running'
    })

def train_fresh_model():
    """Train model with latest data from Supabase and cache it"""
    df = get_revenue_data()
    
    if df is None or len(df) < 10:
        raise Exception('Insufficient data for training')
    
    model = RevenuePredictionModel()
    metrics = model.train(df)
    
    # Cache model in memory
    model_cache['model'] = model
    model_cache['trained_at'] = datetime.now()
    model_cache['data_size'] = len(df)
    
    return model, metrics, len(df)

@app.route('/api/train', methods=['GET', 'POST'])
def train_model():
    """Train the model with latest data from Supabase"""
    try:
        model, metrics, data_size = train_fresh_model()
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully with fresh data',
            'metrics': {
                'mae': float(metrics['mae']),
                'rmse': float(metrics['rmse']),
                'r2': float(metrics['r2']),
                'mape': float(metrics['mape'])
            },
            'training_data_size': data_size,
            'trained_at': model_cache['trained_at'].isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predict', methods=['GET'])
def predict_revenue():
    """Predict future revenue with fresh data from Supabase"""
    try:
        # Get number of days from query parameter (default 30)
        days = request.args.get('days', default=30, type=int)
        
        # Always train with fresh data for realtime predictions
        model, metrics, data_size = train_fresh_model()
        
        # Predict future
        predictions = model.predict_future(days=days)
        
        # Get fitted values (model predictions on training data) for overlay
        fitted_values = model.get_fitted_values()
        
        # Get MAE for confidence bounds
        mae = float(metrics['mae'])
        
        # Convert to list of dicts
        predictions_list = predictions.to_dict('records')
        
        # Format dates and add confidence bounds
        for pred in predictions_list:
            pred['date'] = pred['date'].strftime('%Y-%m-%d')
            pred['predicted_revenue'] = float(pred['predicted_revenue'])
            # Add upper and lower bounds
            pred['upper_bound'] = float(pred['predicted_revenue'] + mae)
            pred['lower_bound'] = float(max(0, pred['predicted_revenue'] - mae))  # Prevent negative
        
        # Convert fitted values to list of dicts
        fitted_list = fitted_values.to_dict('records')
        for fit in fitted_list:
            fit['date'] = fit['date'].strftime('%Y-%m-%d')
            fit['actual_revenue'] = float(fit['actual_revenue'])
            fit['fitted_revenue'] = float(fit['fitted_revenue'])
        
        return jsonify({
            'success': True,
            'predictions': predictions_list,
            'fitted_values': fitted_list,  # Model predictions on training data for overlay
            'summary': {
                'total_predicted': float(predictions['predicted_revenue'].sum()),
                'average_daily': float(predictions['predicted_revenue'].mean()),
                'days': days
            },
            'model_info': {
                'trained_with_data_size': data_size,
                'mae': float(metrics['mae']),
                'rmse': float(metrics['rmse']),
                'r2': float(metrics['r2']),
                'mape': float(metrics['mape'])
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/historical', methods=['GET'])
def get_historical_data():
    """Get historical revenue data"""
    try:
        df = get_revenue_data()
        
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Could not fetch data from Supabase'
            }), 500
        
        # Convert to list of dicts
        historical_list = df.to_dict('records')
        
        # Format dates as strings
        for item in historical_list:
            item['date'] = item['date'].strftime('%Y-%m-%d')
            item['revenue'] = float(item['revenue'])
        
        return jsonify({
            'success': True,
            'data': historical_list,
            'summary': {
                'total_days': len(df),
                'total_revenue': float(df['revenue'].sum()),
                'average_daily': float(df['revenue'].mean()),
                'min_revenue': float(df['revenue'].min()),
                'max_revenue': float(df['revenue'].max())
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
# Inisialisasi Bot (Hanya sekali saat server nyala)
bot = LaundryChatbot()

@app.route('/api/chatbot/reload', methods=['GET', 'POST'])
def reload_chatbot():
    """Reload chatbot FAQ data from Supabase"""
    try:
        count = bot.reload_data()
        return jsonify({
            "success": True,
            "message": f"FAQ data reloaded successfully",
            "faq_count": count
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chatbot', methods=['GET', 'POST'])
def chat():
    """Chatbot endpoint for customer inquiries"""
    # Handle GET request - return info
    if request.method == 'GET':
        return jsonify({
            "success": True,
            "message": "Chatbot API is ready",
            "faq_count": len(bot.df) if bot.df is not None else 0,
            "usage": {
                "method": "POST",
                "endpoint": "/api/chatbot",
                "body": {
                    "message": "your question here"
                }
            }
        })
    
    # Handle POST request - process chat
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                "success": True,
                "reply": "Halo! Ada yang bisa saya bantu?",
                "sender": "bot"
            })
        
        # Minta jawaban ke bot
        reply = bot.get_response(user_message)
        
        return jsonify({
            "success": True,
            "reply": reply,
            "sender": "bot"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "reply": "Maaf, terjadi kesalahan sistem. Silakan coba lagi."
        }), 500
    
@app.route('/api/inventory-prediction', methods=['GET'])
def get_inventory_prediction():
    """Predict inventory stock depletion using Moving Average"""
    try:
        predictor = InventoryPredictor()
        result = predictor.get_prediction()
        
        # Check if error returned from predictor
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'predictions': result,
            'method': 'Moving Average',
            'description': 'Prediksi berdasarkan rata-rata pemakaian harian dari 100 transaksi terakhir'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Revenue Prediction API...")
    print("API Endpoints:")
    print("  GET  /api/health                - Health check")
    print("  GET  /api/train                 - Train model with fresh data from Supabase")
    print("  GET  /api/predict               - Get realtime predictions (auto-trains with latest data)")
    print("  GET  /api/historical            - Get historical revenue data")
    print("  GET  /api/inventory-prediction  - Predict inventory stock depletion (Moving Average)")
    print("  POST /api/chatbot               - Chatbot for customer inquiries")
    print("  GET  /api/chatbot/reload        - Reload FAQ data from Supabase")
    print("\n✅ Realtime mode: Model trains fresh from Supabase for each prediction")
    print("✅ No .pkl files needed - always using latest data")
    print("✅ Chatbot ready with FAQ knowledge base")
    print("✅ Inventory prediction ready with Moving Average\n")
    
    # Get PORT from environment (Render, Railway, etc)
    port = int(os.environ.get('PORT', 5000))
    print(f"Server running on port {port}")
    
    app.run(debug=False, host='0.0.0.0', port=port)
