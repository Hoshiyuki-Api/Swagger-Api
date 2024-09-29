import requests
from flask import Blueprint, jsonify, request
import json, instaloader, uuid
from datetime import datetime
import os
from flask_restx import Namespace, Resource, fields
from requests_toolbelt.multipart.encoder import MultipartEncoder

igstalk_bp = Blueprint('igstalk', __name__)
remove_bp = Blueprint('removebg', __name__)
cuaca_bp = Blueprint('cuaca', __name__)
ffstalk_bp = Blueprint('ffstalk', __name__)

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
removebgrek = Namespace('tools', description='Tools Api')
cuacarek = Namespace('tools', description='Tools Api')
ffstalkgrek = Namespace('tools', description='Tools Api')


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

        if not username:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'username' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        # Periksa dan perbarui batas permintaan
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]
        
        try:
            url = f'https://www.instagram.com/{username}/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', text=lambda t: t and 'window._sharedData' in t).string
            shared_data = script_tag.split(' = ', 1)[1].rstrip(';')
            
            profile_data = json.loads(shared_data)['entry_data']['ProfilePage'][0]['graphql']['user']
            
            username_ = profile_data['username']
            full_name = profile_data['full_name']
            id_ = profile_data['id']
            bio = profile_data['biography']
            follower = profile_data['edge_followed_by']['count']
            followed = profile_data['edge_follow']['count']
            profile_pic = profile_data['profile_pic_url_hd']
            total_post = profile_data['edge_owner_to_timeline_media']['count']
            external_url = profile_data.get('external_url')
            
            return jsonify({
                'a_username': '@' + username_,
                'b_full_name': full_name,
                'c_id': id_,
                'd_biography': bio,
                'e_total_follower': follower,
                'f_total_followed': followed,
                'g_post_total': total_post,
                'h_profile_pic': profile_pic,
                'i_external_url': external_url
            })
        
        except requests.exceptions.RequestException as e:
            return jsonify({"creator": "AmmarBN", "error": str(e)})
        except Exception as e:
            return jsonify({"creator": "AmmarBN", "error": "Failed to parse profile data"})

# Function to remove background using remove.bg and upload to Telegraph
def remove_bg_and_upload(url):
    try:
        # Step 1: Remove background using remove.bg API
        form_data = MultipartEncoder(
            fields={
                'size': 'auto',
                'image_url': url
            }
        )
        
        response_bg = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            data=form_data,
            headers={
                'Content-Type': form_data.content_type,
                'X-Api-Key': 'ueY3nNbPaPcd9kqRxBCPEMQb'
            }
        )
        
        if response_bg.status_code == 200:
            # Step 2: Upload processed image to Telegraph
            url_telegraph = upload_to_telegraph(response_bg.content)
            return {'image_url': 'https://telegra.ph/'+url_telegraph}
        else:
            return {'status': False, 'msg': 'Failed to remove background with remove bg'}
    
    except Exception as e:
        return {'status': False, 'msg': f'Error: {str(e)}'}

# Function to upload image to Telegraph
def upload_to_telegraph(file):
    try:
        url = 'https://telegra.ph/upload'
        files = {'file': ('image.jpg', file, 'image/jpeg')}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            # Get URL from the JSON response
            image_url = response.json()[0]['src']
            return image_url
        else:
            return None
    
    except Exception as e:
        print(f"Error uploading image to Telegraph: {str(e)}")
        return None

@removebgrek.route('')
class Resourcermbg(Resource):
    @removebgrek.doc(params={
        'url': 'Input Url Image',
        'apikey': 'API key for authenticated'
    })
    def get(self):
        """
        Tools Remove Background Image.

        Parameters:
        - url: Url Image (required)
        - apikey: API Key for authentication (required)
        """
        
        image_url = request.args.get('url')
        apikey = request.args.get('apikey')

        if not image_url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        # Periksa dan perbarui batas permintaan
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]

        try:
            # Process image and upload
            result = remove_bg_and_upload(image_url)
            return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'result': result
            })
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

@cuacarek.route('')
class Resourcecauaca(Resource):
    @cuacarek.doc(params={
        'query': 'Input query'
    })
    def get(self):
        """
        Tools Remove Background Image.

        Parameters:
        - query: query (required)
        """
        
        query = request.args.get('query')
        url = f"https://api.shecodes.io/weather/v1/current?query={query}&key=96f59ob69a32facbb34b2tdb5d2e7405"
        response = requests.get(url)
        data = response.json()
        city = data['city']
        country = data['country']
        coordinates = data['coordinates']
        condition = data['condition']['description']
        temperature = data['temperature']['current']
        
        return jsonify (
            {
                'creator': 'AmmarBN',
                'status': True,
                'result': {
                    'city': city,
                    'country': country,
                    'coordinates': coordinates,
                    'condition': condition,
                    'temperature': temperature
                }
            }
        )

# cdoe check akunff

def ff_stalk(id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "X-Device": uuid.uuid4(),
    }

    try:
        # Get token
        token_response = requests.post(
            "https://api.duniagames.co.id/api/item-catalog/v1/get-token",
            json={"msisdn": "0812665588"},
            headers=headers
        )
        token_data = token_response.json()
        token = token_data.get('data', {}).get('token')

        # Perform the inquiry
        inquiry_response = requests.post(
            "https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store",
            json={
                "productId": 3,
                "itemId": 353,
                "product_ref": "REG",
                "product_ref_denom": "REG",
                "catalogId": 376,
                "paymentId": 1252,
                "gameId": id,
                "token": token,
                "campaignUrl": "",
            },
            headers=headers
        )
        inquiry_data = inquiry_response.json()

        game_detail = inquiry_data.get('data', {}).get('gameDetail', {})
        user_name = game_detail.get('userName')

        return user_name
    except Exception as e:
        raise e

@ffstalkgrek.route('')
class Resourceffstalk(Resource):
    @ffstalkgrek.doc(params={
        'id': 'Input Id FreeFire',
        'apikey': 'API key for authenticated'
    })
    def get(self):
        """
        Tools Stalk FreeFire.

        Parameters:
        - id: Id FreeFire (required)
        - apikey: API Key for authentication (required)
        """
        
        Id_ff = request.args.get('id')
        apikey = request.args.get('apikey')

        if not username:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'username' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        # Periksa dan perbarui batas permintaan
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]
        
        try:
            result = ff_stalk(Id_ff)
            return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'id': Id_ff,
                'nikname': result
            })
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})
