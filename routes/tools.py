import requests
from flask import Blueprint, jsonify, request
import json, instaloader
from datetime import datetime
import os
from flask_restx import Namespace, Resource, fields

igstalk_bp = Blueprint('igstalk', __name__)
simitool_bp = Blueprint('simi', __name__)
osmage_bp  = Blueprint('OsintImage', __name__)

# Path ke file database users
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
stalkigrek = Namespace('tools', description='Tools Api')

@stalkigrek.route('')
class Resourceigstalk(Resource):
    @stalkigrek.doc(params={
        'username': 'Input Instagram Username',
        'apikey': 'API key for authenticated'
    })

    def get(self):
        """
        Tools Stalk Instagram.

        Parameters:
        - username: Username Instagram (required)
        - apikey: API Key for authentication (required)
        """
        
        username = request.args.get('username')
        apikey = request.args.get('apikey')

        Lmao = instaloader.Instaloader()
        
        if not username:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'username' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        # Periksa dan perbarui batas permintaan
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]
        
        # Load Profile Dari Instaloader
        profile = instaloader.Profile.from_username(Lmao.context, username)

        # Extract necessary fields from the user object
        username_ = profile.username
        full_name = profile.full_name
        id_ = profile.userid
        bio = profile.biography
        follower = profile.followers
        followed = profile.followees
        profile_pic = profile.profile_pic_url
        total_post = profile.mediacount
        blocked = profile.blocked_by_viewer
        external_url = profile.external_url

        # Ensure all returned data is JSON serializable
        return jsonify({
            'a_username': '@'+username_,
            'b_full_name': full_name,
            'c_id': id_,
            'd_biography': bio,
            'e_total_follower': follower,
            'f_total_followed': followed,
            'g_post_total': total_post,
            'h_profile_pic': profile_pic,
            'i_block_you': blocked,
            'j_external_url': external_url
        })


@simitool_bp.route('/api/tools/simi', methods=['GET'])
def igstalk():
    text= request.args.get('text')
    apikey = request.args.get('apikey')
    
    if not text:
        return jsonify({"creator": "AmmarBN", "error": "Parameter 'text' diperlukan."})

    if apikey is None:
        return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
    
    # Periksa dan perbarui batas permintaan
    limit_error = check_and_update_request_limit(apikey)
    if limit_error:
        return jsonify(limit_error[0]), limit_error[1]
    
    a = requests.post("https://simsimi.vn/web/simtalk",
	headers={
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://simsimi.vn/'
	},
	data={
		'text':text,
		'lc':'id'
    }
    ).text

    return jsonify(
        {
            'creator': 'AmmarBN',
            'status': True,
            'result': a
        }
    )

@osmage_bp.route('/api/tools/osmage', methods=['GET'])
def osmage():
    url = request.args.get('url')
    apikey = request.args.get('apikey')
    
    if not url:
        return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

    if apikey is None:
        return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
    
    # Periksa dan perbarui batas permintaan
    limit_error = check_and_update_request_limit(apikey)
    if limit_error:
        return jsonify(limit_error[0]), limit_error[1]
    
    headers = {
    'authority': 'locate-image-7cs5mab6na-uc.a.run.app',
    'accept': '*/*',
    'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://geospy.ai',
    'referer': 'https://geospy.ai/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    
    filename = url
    response = requests.get(filename)

    # Infer the content type from the file extension
    if filename.endswith('jpg') or filename.endswith('jpeg'):
        content_type = 'image/jpeg'
    elif filename.endswith('png'):
        content_type = 'image/png'
    else:
        content_type = 'application/octet-stream'

    files = {
    'image': ('image_file', response.content, content_type),
    }

    response = requests.post('https://locate-image-7cs5mab6na-uc.a.run.app/', headers=headers, files=files)
    data = response.json()

    # Extract the required information safely
    message_lines = data.get("message", "").split("\n")
    country = message_lines[0].split(": ")[1] if len(message_lines) > 0 and ": " in message_lines[0] else "N/A"
    state = message_lines[1].split(": ")[1] if len(message_lines) > 1 and ": " in message_lines[1] else "N/A"
    city = message_lines[2].split(": ")[1] if len(message_lines) > 2 and ": " in message_lines[2] else "N/A"
    explanation = message_lines[3].split(": ")[1] if len(message_lines) > 3 and ": " in message_lines[3] else "N/A"
    coordinates = message_lines[4].split(": ")[1] if len(message_lines) > 4 and ": " in message_lines[4] else "N/A"
    print (coordinates)
    print (explanation)
    print (state)

    return jsonify(
        {
            'creator': 'AmmarBN',
            'status': True,
            'result': {
                'country': country,
                'state': state,
                'city': city,
                'coordinate': coordinates,
                'explanation': explanation
            }
        }
    )
