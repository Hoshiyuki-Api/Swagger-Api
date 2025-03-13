from flask import Blueprint, jsonify, request
import requests, json, user_agent, os, sys
from datetime import datetime
from flask_restx import Namespace, Resource, fields

jadwalsholat_bp = Blueprint('jadwalsholat', __name__)

users_db = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.json')

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
sholat = Namespace('JadwalSholat', description='API untuk mendapatkan jadwal sholat berdasarkan kota')

# Model untuk response jadwal sholat
jadwal_sholat_model = api.model('JadwalSholat', {
    'Creator': fields.String(description='Creator information'),
    'Jadwal': fields.Raw(description='Detail jadwal sholat')
})

# Endpoint untuk mendapatkan jadwal sholat
@api.route('')
class PrayerTimesResource(Resource):
    @api.doc(params={
        'kota': 'Nama kota untuk mencari ID kota',
        'id': 'ID kota untuk mendapatkan jadwal sholat'
    })
    def get(self):
        """
        Mengembalikan jadwal sholat berdasarkan kota atau ID kota.

        Parameters:
        - kota: Nama kota untuk mencari ID kota (opsional)
        - id: ID kota untuk mendapatkan jadwal sholat (opsional)

        Returns:
        - Jika hanya kota diberikan, API mengembalikan daftar kota yang cocok.
        - Jika ID kota diberikan, API mengembalikan jadwal sholat untuk hari ini.
        """
        keyword = request.args.get('kota', default='', type=str)
        city_id = request.args.get('id', default='', type=str)

        try:
            if not keyword:
                # Jika keyword tidak diberikan, ambil semua daftar kota dari API
                api_url = 'https://api.myquran.com/v2/sholat/kota/cari/kota'
                get_api = requests.get(api_url).json()
                return jsonify(get_api)
            elif keyword and not city_id:
                # Jika hanya keyword yang diberikan, cari kota berdasarkan nama
                api_url = f'https://api.myquran.com/v2/sholat/kota/cari/{keyword}'
                get_api = requests.get(api_url).json()
                return jsonify(get_api)
            elif keyword and city_id:
                # Ambil tanggal hari ini
                today_date = datetime.now().date()

                # Request jadwal sholat berdasarkan ID kota dan tanggal
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
