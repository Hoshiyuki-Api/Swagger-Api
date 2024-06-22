import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from collections import OrderedDict

check_bp = Blueprint('check', __name__)

# Path to the users database file
users_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.json')

@check_bp.route('/check', methods=['GET'])
def check_user():
    # Get ID and API key from query string parameters
    user_id = request.args.get('id')
    api_key = request.args.get('api_key')

    if not user_id and not api_key:
        return jsonify({"error": "Please provide a user ID or API key"}), 400

    # Read user data from the JSON file
    with open(users_db, 'r') as f:
        users = json.load(f, object_pairs_hook=OrderedDict)

    found_user = None

    # Find user data based on user ID
    if user_id:
        for username, user_data in users.items():
            if str(user_data.get('id')) == user_id:
                found_user = user_data
                found_user['username'] = username
                break

    # Find user data based on API key
    if not found_user and api_key:
        for user_data in users.values():
            if user_data.get('api_key') == api_key:
                found_user = user_data
                break

    if found_user:
        # Check if the API key has expired
        expired_date = datetime.strptime(found_user.get('expired_date'), '%d-%m-%Y')
        if expired_date < datetime.now():
            return jsonify({"error": "API key has expired"}), 403

        # Check and display remaining request limit
        request_limit = found_user.get('request_limit', {})
        remaining_requests = 30 - request_limit.get('count', 0)
        if remaining_requests < 0:
            remaining_requests = 0
        
        # Display user details
        user_details = OrderedDict()
        user_details["Id"] = found_user.get('id')
        user_details["Username"] = found_user.get('username', '')
        user_details["Email"] = found_user.get('email', '')
        user_details["Expired"] = found_user.get('expired_date', '')
        user_details["Api_Key"] = found_user.get('api_key', '')
        user_details["Remaining_Requests"] = remaining_requests

        return jsonify(user_details), 200
    else:
        return jsonify({"error": "Invalid user ID or API key"}), 404
