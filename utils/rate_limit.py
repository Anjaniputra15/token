from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from supabase_client import supabase

def rate_limiter(f):
    @wraps(f)
    def decorated_function(client, *args, **kwargs):
        try:
            # Get current usage
            period_seconds = client['rate_limit_period']
            cutoff = datetime.now() - timedelta(seconds=period_seconds)
            
            usage = supabase.table('client_usage') \
                .select('count', count='exact') \
                .gt('timestamp', cutoff.isoformat()) \
                .eq('client_id', client['id']) \
                .execute()
            
            request_count = usage.count
            
            # Check quota
            if request_count >= client['quota_limit']:
                return jsonify({
                    'error': f"Rate limit exceeded ({client['quota_limit']} requests per {client['rate_limit_period']}s)"
                }), 429
                
            # Log request
            supabase.table('client_usage').insert({
                'client_id': client['id'],
                'endpoint': request.path
            }).execute()
            
            request.environ['rate_limit_remaining'] = client['quota_limit'] - request_count - 1
            
            return f(client, *args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return decorated_function