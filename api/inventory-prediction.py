from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add api folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from inventory import InventoryPredictor
    
    def get_inventory_prediction():
        """Get inventory prediction with error handling"""
        try:
            predictor = InventoryPredictor()
            result = predictor.get_prediction()
            
            # Handle case where result might be an error dict
            if isinstance(result, dict) and "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                    "predictions": []
                }
            
            # Validate result is a list
            if not isinstance(result, list):
                return {
                    "success": False,
                    "error": "Invalid prediction data format",
                    "predictions": []
                }
            
            return {
                "success": True,
                "predictions": result,
                "total_items": len(result)
            }
            
        except Exception as error:
            print(f"Error in inventory prediction: {error}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to generate inventory prediction: {str(error)}",
                "predictions": []
            }
    
except Exception as error:
    print(f"Import error: {error}")
    def get_inventory_prediction():
        return {
            "success": False,
            "error": f"Server configuration error: {str(error)}",
            "predictions": []
        }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get inventory prediction
            result = get_inventory_prediction()
            
            # Determine status code
            status_code = 200 if result.get('success') else 500
            
            # Send response
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=180')  # Cache for 3 minutes
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as error:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(error),
                'predictions': []
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
