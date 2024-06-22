from flask import Blueprint, request, jsonify, session
import os
import uuid
import json
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Path to the users database file
users_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.json')

# Function to create users.json file if it doesn't exist
def create_users_file():
    if not os.path.exists(users_db):
        with open(users_db, 'w') as f:
            json.dump({}, f)

# Create users.json file if it doesn't exist
create_users_file()

# Register endpoint
@auth_bp.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    expired_date = request.form.get('expired_date')

    if not email or not username or not password or not expired_date:
        return jsonify({"error": "Missing username, email, password, or expired date"}), 400

    # Validate expired date format
    try:
        expired_date_obj = datetime.strptime(expired_date, '%d-%m-%Y')
    except ValueError:
        return jsonify({"error": "Invalid expired date format, should be DD-MM-YYYY"}), 400

    # Read existing users data
    with open(users_db, 'r') as f:
        users = json.load(f)

    # Check if email or username already exist
    # Check if email or username already exist
    for user_key in users.keys():  # Loop melalui kunci pengguna
        user = users[user_key]  # Dapatkan data pengguna dengan menggunakan kunci
        if user['email'] == email:
            return jsonify({"error": "Email telah digunakan"}), 400
        if user_key == username:  # Gunakan kunci pengguna langsung
            return jsonify({"error": "Username telah digunakan"}), 400


    # Generate unique API key
    api_key = str(uuid.uuid4())

    # If no users exist, set initial max_id to 0
    if not users:
        max_id = 0
    else:
        max_id = max(users.values(), key=lambda x: x.get('id', 0)).get('id', 0)

    # Add user to database
    new_id = max_id + 1
    users[username] = {
        'id': new_id,
        'email': email,
        'password': password,
        'expired_date': expired_date,
        'api_key': "yk-" + api_key,
        'request_limit': {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'count': 0
        }
    }

    # Write the updated users data back to the database file
    with open(users_db, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"message": "User registered successfully", "api_key": api_key}), 201

# Login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Read existing users data
    with open(users_db, 'r') as f:
        users = json.load(f)

    # Check if the username and password match
    if username not in users or users[username]['password'] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    # Set user's login status
    session['logged_in'] = True
    session['username'] = username

    return jsonify({"message": "Login successful", "api_key": users[username]['api_key']}), 200
