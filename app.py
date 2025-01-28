

from flask import Flask, request, jsonify
from supabase import create_client  # Make sure the correct import is used
from utils.auth import generate_api_key, hash_api_key, authenticate
from utils.rate_limit import rate_limiter
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("JWT_SECRET")

# Supabase Configuration (replace with actual environment variables or config)
url = os.environ.get("SUPABASE_URL")  # Make sure this is set in your environment
key = os.environ.get("SUPABASE_KEY")  # Make sure this is set in your environment
supabase = create_client(url, key)

# Routes
@app.route('/api/clients', methods=['POST'])
def create_client_route():
    api_key = generate_api_key()
    data = request.json or {}
    
    try:
        response = supabase.table('clients').insert({
            'api_key_hash': hash_api_key(api_key),
            'quota_limit': data.get('quota_limit', 100),
            'rate_limit_period': data.get('rate_limit_period', 3600),
            'metadata': data.get('metadata', {})
        }).execute()
        
        return jsonify({
            'client_id': response.data[0]['id'],
            'api_key': api_key,
            'warning': 'Store this API key securely!'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['GET'])
@authenticate
@rate_limiter
def protected_data(client):
    return jsonify({
        'message': 'Protected data',
        'client_id': client['id'],
        'remaining': request.environ.get('rate_limit_remaining')
    })

if __name__ == '__main__':
    app.run(port=int(os.environ.get("FLASK_PORT", 5000)))

# Add more routes as needed