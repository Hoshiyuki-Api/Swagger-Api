from flask import Blueprint, jsonify, request
import json
from datetime import datetime
import os
import user_agent  # Pastikan Anda memiliki library user_agent yang diimpor
from flask_restx import Namespace, Resource, fields

# Blueprint untuk useragent
useragent_bp = Blueprint('useragent', __name__)

# Path ke file database users
users_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.json')

# Fungsi untuk menghasilkan user agent
def generate_user_agent():
    return user_agent.generate_user_agent()

# Helper function to check if apikey is expired
def check_apikey_expiry(apikey):
    # Read existing users data
    with open(users_db, 'r') as f:
        users = json.load(f)

    username = None
    for user, data in users.items():
        if data.get('api_key') == apikey:
            username = user
            break

    if username is None:
        return {"error": "API key tidak valid", "error_code": 401}, 401

    user = users.get(username)
    if not user:
        return {"error": "Pengguna tidak ditemukan", "error_code": 404}, 404

    # Check if the apikey has expired
    expired_date = datetime.strptime(user['expired_date'], '%d-%m-%Y').date()
    today = datetime.now().date()
    if expired_date < today:
        return {"error": "Apikey Anda Telah Kadaluarsa", "error_code": 403}, 403

    return None

# Helper function to check and update request limit
def check_and_update_request_limit(apikey):
    today = datetime.now().strftime('%Y-%m-%d')

    # Check if apikey is expired
    expiry_error = check_apikey_expiry(apikey)
    if expiry_error:
        return expiry_error

    # Read existing users data
    with open(users_db, 'r') as f:
        users = json.load(f)

    username = None
    for user, data in users.items():
        if data.get('api_key') == apikey:
            username = user
            break

    if username is None:
        return {"error": "API key tidak valid", "error_code": 401}, 401

    user = users.get(username)
    if not user:
        return {"error": "Pengguna tidak ditemukan", "error_code": 404}, 404

    # Initialize request limits if not present
    if 'request_limit' not in user:
        user['request_limit'] = {'date': today, 'count': 0}

    # Check if the request count needs to be reset
    if user['request_limit']['date'] != today:
        user['request_limit'] = {'date': today, 'count': 0}

    # Check if the limit has been exceeded
    if user['request_limit']['count'] >= 1000:
        return {"error": "Apikey anda telah mencapai Limit", "error_code": 429}, 429

    # Increment the request count
    user['request_limit']['count'] += 1

    # Write the updated users data back to the database file
    with open(users_db, 'w') as f:
        json.dump(users, f, indent=4)

    return None

# Namespace untuk Flask-RESTX
api = Namespace('API', description='Generate random user agents')

# Model untuk response user agents
user_agent_model = api.model('UserAgent', {
    'user_agents': fields.List(fields.String, description='List of generated User-Agents'),
    'pembuat': fields.String(description='Creator information')
})

# Endpoint untuk menghasilkan user agents acak
@api.route('')
class UserAgentResource(Resource):
    @api.doc(params={
        'jum': 'Number of User-Agents to return',
        'apikey': 'API Key for authentication'
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Returns a list of random User-Agents.

        Parameters:
        - jum: Number of User-Agents to return (required)
        - apikey: API Key for authentication (required)

        Returns:
        - user_agents: List of generated User-Agents
        - pembuat: Creator information
        """
        num_ua = request.args.get('jum', default=None, type=int)
        apikey = request.args.get('apikey')

        if num_ua is None:
            return {"pembuat": "AmmarBN", "error": "Parameter 'jum' diperlukan."}, 400

        if apikey is None:
            return {"pembuat": "AmmarBN", "error": "Parameter 'apikey' diperlukan."}, 400

        # Periksa dan perbarui batas permintaan
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return limit_error[0], limit_error[1]

        # Hasilkan user agents
        user_agents = [generate_user_agent() for _ in range(num_ua)]
        return {"user_agents": user_agents, "pembuat": "AmmarBN"}, 200

