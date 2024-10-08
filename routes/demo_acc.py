import os
import json
from flask import Blueprint, jsonify

# Initialize Blueprint
users_demo_bp = Blueprint('users_demo', __name__)

# Path to the ID database file
demo_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'demo.json')

# Route to return data from id.json
@users_demo_bp.route('/exec/ryochi/app/hidden/demo', methods=['GET'])
def get_users_data():
    """
    Returns the content of the id.json file.
    
    Returns:
    - JSON data from demo.json
    """
    try:
        # Read the data from the id.json file
        with open(demo_db, 'r') as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return {"error": "ID database not found"}, 500
