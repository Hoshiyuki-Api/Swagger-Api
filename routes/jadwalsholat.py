from flask import Blueprint, jsonify, request
import requests, json, user_agent
from datetime import datetime

jadwalsholat_bp = Blueprint('jadwalsholat', __name__)

@jadwalsholat_bp.route('/jadwalsholat', methods=['GET'])
def get_prayer_times():
    keyword = request.args.get('kota', default='', type=str)
    city_id = request.args.get('id', default='', type=str)

    try:
        if not keyword:
            # If keyword is not provided, fetch data from the specified API endpoint
            api_url = 'https://api.myquran.com/v2/sholat/kota/cari/kota'
            get_api = requests.get(api_url).json()
            return jsonify(get_api)
        elif keyword and not city_id:
            # API request for keyword only
            api_url = f'https://api.myquran.com/v2/sholat/kota/cari/{keyword}'
            get_api = requests.get(api_url).json()
            return jsonify(get_api)
        elif keyword and city_id:
            # Get today's date
            today_date = datetime.now().date()

            # API request for city, id, and today's date
            api_url = f'https://api.myquran.com/v2/sholat/jadwal/{city_id}/{today_date.year}/{today_date.month}/{today_date.day}'
            data = requests.get(api_url).json()

            if 'data' in data and 'jadwal' in data['data']:
                jadwal = data['data']['jadwal']
                return jsonify({"Creator": "AmmarBN", "Jadwal": jadwal})
            else:
                return jsonify({"Creator": "AmmarBN", "response": "Invalid Response structure"})
        else:
            return jsonify({'status': False, 'error': 'Invalid parameters'})
    
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)})
