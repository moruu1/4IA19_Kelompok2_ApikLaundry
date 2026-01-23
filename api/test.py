from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Return simple JSON
        response = {
            'success': True,
            'message': 'Python API is working on Vercel!',
            'endpoint': '/api/test'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
