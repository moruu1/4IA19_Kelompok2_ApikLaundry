from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add api folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from fetch_data import get_revenue_data
    
    def get_historical_data():
        """Get historical revenue data with error handling"""
        try:
            data = get_revenue_data()
            
            if not data:
                return {
                    "success": False,
                    "error": "No historical data available",
                    "data": []
                }
            
            # Convert date objects to strings for JSON serialization
            serialized_data = []
            for item in data:
                serialized_item = {
                    'date': item['date'].isoformat() if hasattr(item['date'], 'isoformat') else str(item['date']),
                    'revenue': float(item['revenue'])
                }
                serialized_data.append(serialized_item)
            
            return {
                "success": True,
                "data": serialized_data,
                "total_records": len(serialized_data)
            }
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to fetch historical data: {str(e)}",
                "data": []
            }
    
except Exception as e:
    print(f"Import error: {e}")
    def get_historical_data():
        return {
            "success": False,
            "error": f"Server configuration error: {str(e)}",
            "data": []
        }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get historical data
            result = get_historical_data()
            
            # Determine status code
            status_code = 200 if result.get('success') else 500
            
            # Send response
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=300')  # Cache for 5 minutes
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e),
                'data': []
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
