from flask import Flask, jsonify

app = Flask(__name__)

def handler(request):
    """Vercel serverless function handler"""
    return jsonify({
        'status': 'ok',
        'message': 'ML API is running on Vercel',
        'endpoint': '/api/health'
    })
