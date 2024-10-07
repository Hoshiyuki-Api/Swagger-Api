import os
import json
from flask import Blueprint, jsonify

# Initialize Blueprint
users_data_bp = Blueprint('users_data', __name__)

# Path to the ID database file
id_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'id.json')

# Route to return data from id.json
@users_data_bp.route('/users/data/get', methods=['GET'])
def get_users_data():
    """
    Returns the content of the id.json file.
    
    Returns:
    - JSON data from id.json
    """
    try:
        # Read the data from the id.json file
        with open(id_db, 'r') as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return {"error": "ID database not found"}, 500
