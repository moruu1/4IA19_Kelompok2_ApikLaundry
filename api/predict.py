from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
import os
import sys

# Add api folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import from original app
try:
    from flask import Flask
    from flask_cors import CORS
    from model import RevenuePredictionModel
    from fetch_data import get_revenue_data
    
    app = Flask(__name__)
    CORS(app)
    
    def train_and_predict(days=30):
        """Train model and get predictions"""
        df = get_revenue_data() # This now returns list of dicts
        
        if df is None or len(df) < 5:
            raise Exception('Insufficient data for training')
        
        model = RevenuePredictionModel()
        metrics = model.train(df)
        
        # model.predict_future returns dict with 'predictions' list
        future_result = model.predict_future(days=days)
        predictions_list = future_result['predictions']
        
        # model.get_fitted_values returns list of dicts
        fitted_list = model.get_fitted_values()
        
        mae = float(metrics['mae'])
        
        # Format predictions (add upper/lower bound)
        formatted_predictions = []
        for pred in predictions_list:
            # pred['date'] is already isoformat string from model.predict_future
            val = float(pred['predicted_revenue'])
            formatted_predictions.append({
                'date': pred['date'],
                'predicted_revenue': val,
                'upper_bound': val + mae,
                'lower_bound': max(0, val - mae)
            })
        
        # Format fitted values
        formatted_fitted = []
        for fit in fitted_list:
            formatted_fitted.append({
                'date': fit['date'].strftime('%Y-%m-%d'),
                'actual_revenue': float(fit['actual_revenue']),
                'fitted_revenue': float(fit['fitted_revenue'])
            })
        
        return {
            'success': True,
            'predictions': formatted_predictions,
            'fitted_values': formatted_fitted,
            'summary': {
                'total_predicted': float(future_result['total_predicted']),
                'average_daily': float(future_result['average_daily']),
                'days': days
            },
            'model_info': {
                'trained_with_data_size': len(df),
                'mae': float(metrics['mae']),
                'rmse': float(metrics['rmse']),
                'r2': float(metrics['r2']),
                'mape': float(metrics['mape'])
            }
        }
        
except Exception as e:
    print(f"Import error: {e}")
    def train_and_predict(days=30):
        return {'success': False, 'error': str(e)}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed = urlparse(self.path)
            query_params = parse_qs(parsed.query)
            days = int(query_params.get('days', ['30'])[0])
            
            # Get predictions
            result = train_and_predict(days)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
