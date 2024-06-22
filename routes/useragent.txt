from flask import Blueprint, jsonify, request
import json, user_agent
from datetime import datetime
import os

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
    if user['request_limit']['count'] >= 30:
        return {"error": "Apikey anda telah mencapai Limit", "error_code": 429}, 429

    # Increment the request count
    user['request_limit']['count'] += 1

    # Write the updated users data back to the database file
    with open(users_db, 'w') as f:
        json.dump(users, f, indent=4)

    return None

# Endpoint untuk menghasilkan user agents acak
@useragent_bp.route('/user-agent', methods=['GET'])
def generate_random_user_agents():
    num_ua = request.args.get('jum', default=None, type=int)
    apikey = request.args.get('apikey')

    if num_ua is None:
        return jsonify({"pembuat": "AmmarBN", "error": "Parameter 'jum' diperlukan."})

    if apikey is None:
        return jsonify({"pembuat": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})

    # Periksa dan perbarui batas permintaan
    limit_error = check_and_update_request_limit(apikey)
    if limit_error:
        return jsonify(limit_error[0]), limit_error[1]

    # Hasilkan user agents
    user_agents = [generate_user_agent() for _ in range(num_ua)]
    return jsonify({"user_agents": user_agents, "pembuat": "AmmarBN"}), 200
