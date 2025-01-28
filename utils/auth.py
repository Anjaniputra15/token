import jwt
import bcrypt
import os
from functools import wraps
from flask import request, jsonify
from supabase_client import supabase

def generate_api_key():
    return f"sk_{os.urandom(24).hex()}"

def hash_api_key(api_key: str) -> str:
    return bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key missing'}), 401
            
        try:
            # Find client by API key
            client = supabase.table('clients') \
                .select('*') \
                .eq('api_key_hash', hash_api_key(api_key)) \
                .single() \
                .execute()
                
            # Generate JWT
            token = jwt.encode({
                'client_id': client.data['id'],
                'quota': client.data['quota_limit'],
                'exp': 900  # 15 minutes
            }, os.environ.get("JWT_SECRET"))
            
            request.environ['client'] = client.data
            request.environ['jwt_token'] = token
            
            return f(client.data, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': 'Invalid API key', 'details': str(e)}), 401
            
    return decorated_function