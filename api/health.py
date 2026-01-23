from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add api folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from config import SUPABASE_URL, SUPABASE_KEY
    from supabase import create_client, Client
    
    def check_database_connection():
        """Check if database connection is working"""
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Simple query to test connection
            response = supabase.table('financials').select('id_transaksi').limit(1).execute()
            return True
        except Exception as e:
            print(f"Database check failed: {e}")
            return False
    
except Exception as e:
    print(f"Import error in health check: {e}")
    def check_database_connection():
        return False


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check database connectivity
            db_status = check_database_connection()
            
            response_data = {
                "status": "ok" if db_status else "degraded",
                "message": "API is running",
                "database": "connected" if db_status else "disconnected",
                "environment": {
                    "supabase_url_configured": bool(SUPABASE_URL),
                    "supabase_key_configured": bool(SUPABASE_KEY)
                }
            }
            
            # Send response
            self.send_response(200 if db_status else 503)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'status': 'error',
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
