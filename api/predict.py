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
        df = get_revenue_data()
        
        if df is None or len(df) < 10:
            raise Exception('Insufficient data for training')
        
        model = RevenuePredictionModel()
        metrics = model.train(df)
        predictions = model.predict_future(days=days)
        fitted_values = model.get_fitted_values()
        mae = float(metrics['mae'])
        
        # Format predictions
        predictions_list = predictions.to_dict('records')
        for pred in predictions_list:
            pred['date'] = pred['date'].strftime('%Y-%m-%d')
            pred['predicted_revenue'] = float(pred['predicted_revenue'])
            pred['upper_bound'] = float(pred['predicted_revenue'] + mae)
            pred['lower_bound'] = float(max(0, pred['predicted_revenue'] - mae))
        
        # Format fitted values
        fitted_list = fitted_values.to_dict('records')
        for fit in fitted_list:
            fit['date'] = fit['date'].strftime('%Y-%m-%d')
            fit['actual_revenue'] = float(fit['actual_revenue'])
            fit['fitted_revenue'] = float(fit['fitted_revenue'])
        
        return {
            'success': True,
            'predictions': predictions_list,
            'fitted_values': fitted_list,
            'summary': {
                'total_predicted': float(predictions['predicted_revenue'].sum()),
                'average_daily': float(predictions['predicted_revenue'].mean()),
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
