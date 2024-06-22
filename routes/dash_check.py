import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from collections import OrderedDict
from flask_restx import Namespace, Resource, fields

check_bp = Blueprint('check', __name__)

# Path to the users database file
users_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.json')

# Namespace untuk Flask-RESTX
api = Namespace('check', description='Endpoint to check user details')

# Model untuk response user details
user_details_model = api.model('UserDetails', {
    'Id': fields.Integer(description='User ID'),
    'Username': fields.String(description='Username'),
    'Email': fields.String(description='Email address'),
    'Expired': fields.String(description='Expiry date of API key'),
    'Api_Key': fields.String(description='API Key'),
    'Remaining_Requests': fields.Integer(description='Remaining API request limit')
})

# Endpoint untuk check user details
@api.route('')
class CheckUser(Resource):
    @api.doc(params={
        'email':'User Email'
    })
    # @api.marshal_with(user_details_model)
    def get(self):
        """
        Check user details based on User ID or API Key.

        Parameters:
        - email: User Email

        Returns:
        - User details if valid
        - Error message if invalid
        """
        email = request.args.get('email')

        if not email:
            return {"error": "Please provide your email"}, 400

        # Read user data from the JSON file
        with open(users_db, 'r') as f:
            users = json.load(f, object_pairs_hook=OrderedDict)

        found_user = None

        for username, user_data in users.items():
            if user_data.get('email') == email:
                found_user = user_data
                found_user['username'] = username
                break

        if found_user:
            # Check if the API key has expired
            expired_date = datetime.strptime(found_user.get('expired_date'), '%d-%m-%Y')
            if expired_date < datetime.now():
                return {"error": "API key has expired"}, 403

            # Check and display remaining request limit
            request_limit = found_user.get('request_limit', {})
            remaining_requests = 30 - request_limit.get('count', 0)
            if remaining_requests < 0:
                remaining_requests = 0
            
            # Prepare user details response
            user_details = {
                "Id": found_user.get('id'),
                "Username": found_user.get('username', ''),
                "Email": found_user.get('email', ''),
                "Expired": found_user.get('expired_date', ''),
                "Api_Key": found_user.get('api_key', ''),
                "Remaining_Requests": remaining_requests
            }

            return user_details, 200
        else:
            return {"error": "Invalid Email"}, 404

# Registrasi Blueprint check_bp
# api.add_resource(CheckUser, '/')  # Atur path ke endpoint

