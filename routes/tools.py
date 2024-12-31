import requests
from flask import Blueprint, jsonify, request
from flask import Response
import json, instaloader, uuid, base64, time
from datetime import datetime
import os
from flask_restx import Namespace, Resource, fields
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup

igstalk_bp = Blueprint('igstalk', __name__)
remove_bp = Blueprint('removebg', __name__)
cuaca_bp = Blueprint('cuaca', __name__)
ffstalk_bp = Blueprint('ffstalk', __name__)
removebg2_bp = Blueprint('removebg2', __name__)
ssweb_bp = Blueprint('ssweb', __name__)
wape_bp = Blueprint('wattpad', __name__)
brat_bp = Blueprint('brat', __name__)
theater_bp = Blueprint('theater', __name__)
glimg_bp  = Blueprint('gimg', __name__)
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
removebg2grek = Namespace('tools', description='Tools Api')
sswebgrek = Namespace('tools', description='Tools Api')
wapegrek = Namespace('tools', description='Tools Api')
bratgrek = Namespace('tools', description='Tools Api')
theatergrek = Namespace('tools', description='Tools Api')
glimggrek = Namespace('tools', description='Tools Api')

@stalkigrek.route('')
class Resourceigstalk(Resource):
    @stalkigrek.doc(params={
        'username': 'Input Instagram Username',
    })
    def get(self):
        """
        Tools Stalk Instagram.

        Parameters:
        - username: Username Instagram (required)
        """
        
        username = request.args.get('username')

        if not username:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'username' diperlukan."})

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
    })
    def get(self):
        """
        Tools Remove Background Image.

        Parameters:
        - url: Url Image (required)
        """
        
        image_url = request.args.get('url')

        if not image_url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

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
        "X-Device": str(uuid.uuid4()),
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
    })
    def get(self):
        """
        Tools Stalk FreeFire.

        Parameters:
        - id: Id FreeFire (required)
        """
        
        Id_ff = request.args.get('id')

        if not Id_ff:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'username' diperlukan."})

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


@removebg2grek.route('')
class Resourceremovebg2(Resource):
    @removebg2grek.doc(params={
        'url': 'Input Url Image',
    })
    def get(self):
        """
        Tools Remove Background Image V2.

        Parameters:
        - url: Url Image (required)
        """
        
        image_url = request.args.get('url')

        if not image_url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

        try:
            filename = image_url
            response = requests.get(filename)

            # Infer the content type from the file extension
            if filename.endswith('jpg') or filename.endswith('jpeg'):
                content_type = 'image/jpeg'
            elif filename.endswith('png'):
                content_type = 'image/png'
            elif filename.endswith('webp'):
                content_type = 'image/webp'
            else:
                content_type = 'application/octet-stream'

            # remove bg
            headers = {
                'authority': 'api2.pixelcut.app',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
                'authorization': '',  # Add your authorization token here
                'origin': 'https://www.pixelcut.ai',
                'referer': 'https://www.pixelcut.ai/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'x-client-version': 'web',
            }

            # Prepare the files and data
            files = {
                'image': ('image_file', response.content, content_type),
            }
            data = {
                'format': 'png',
                'model': 'v1',
            }

            # Send the POST request
            resp = requests.post('https://api2.pixelcut.app/image/matte/v1', headers=headers, files=files, data=data)

            # Save the response as an image file
            if resp.status_code == 200:
                img_base64 = base64.b64encode(resp.content).decode('utf-8')
                return jsonify({
                    'creator': 'AmmarBN',
                    'status': True,
                    'url_img': img_base64,
                })
            else:return jsonify({'status': False, 'msg': f'Error: url image error'})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})


@sswebgrek.route('')
class Resourcessweb(Resource):
    @sswebgrek.doc(params={
        'url': 'Input Url Website',
        'mode': 'Input Mode desktop and mobile',
    })
    def get(self):
        """
        Capture a website screenshot online.

        Parameters:
        - url: Url Website (required)
        - mode: desktop and mobile ssweb
        """
        
        image_url = request.args.get('url')
        mode = request.args.get('mode')

        if not image_url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
        if not mode:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'mode' diperlukan."})

        try:
             unix_timestamp = int(time.time())
             headers = {
               "Host": "demoair-api.wondershare.com",
               "content-length": "103",
               "teams": "teams",
               "accept": "application/json, text/plain, */*",
               "user-agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
               "content-type": "application/json",
               "origin": "https://demoair.wondershare.com",
               "sec-fetch-site": "same-site",
               "sec-fetch-mode": "cors",
               "sec-fetch-dest": "empty",
               "referer": "https://demoair.wondershare.com/",
               "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
             }
             submit_data = {"taskType": 5,"args": {"url": image_url,"fullPage": 1,"type": mode,"outputSuffix": "jpg"}}
             submit_url = f"https://demoair-api.wondershare.com/api/demo/task/submit?_t={unix_timestamp}"
             uid = requests.post(submit_url, headers=headers, data=json.dumps(submit_data)).json()["data"]["taskUuid"]
             progress_url = f"https://demoair-api.wondershare.com/api/demo/task/progress?_t={unix_timestamp}"
             progress_data = {"taskUuid": uid}
             timeout = 30
             interval = 2
             start_time = time.time()
             while time.time() - start_time < timeout:
                  response = requests.post(progress_url, headers=headers, data=json.dumps(progress_data))
                  progress_info = response.json()
                  if 'images' in progress_info['data']['attacheInformation']:
                      res_url = progress_info['data']['attacheInformation']['images']
                      return jsonify({
                        'creator': 'AmmarBN',
                        'status': True,
                        'url_img': res_url #.replace("['", "").replace("']", ""),
                      })
                  time.sleep(interval)
             return jsonify({"status": "in_progress", "message": "Task is still processing. Please check back later."})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

class Wattpad:
    base_url = "https://www.wattpad.com"

    @staticmethod
    def search(query):
        url = f"{Wattpad.base_url}/search/{query}"
        headers = {
    "Host": "www.wattpad.com",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": (
        "wp_id=8e94bf42-cded-4209-9489-c08489bb2f99; "
        "locale=id_ID; lang=1; feat-fedcm-rollout=1; "
        "_gcl_au=1.1.51497984.1732782637; _fbp=fb.1.1732782637433.629470476324396246; "
        "_col_uuid=67823971-6aa8-4d12-9f50-9927894bc3fc-hvfc; _gid=GA1.2.1416226195.1732782638; "
        "adMetrics=0; _pbkvid05_=0; _pbeb_=0; _afp25f_=0; ff=1; dpr=1.75; tz=-7; "
        "X-Time-Zone=Asia%2FJakarta; fs__exp=2; sn__time=j%3Anull; signupFrom=search; "
        "te_session_id=1732850628196; _ga_FNDTZ0MZDQ=GS1.1.1732850629.3.0.1732850629.0.0.0; "
        "AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.1231341048.1732782636; "
        "RT=r=https%3A%2F%2Fwww.wattpad.com%2Fsearch%2Fgood&ul=1732850664985"
    )
        }
        response = requests.get(url, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        results = []
        stories = soup.select("section#section-results-stories article#results-stories ul.list-group li.list-group-item")
#        print (soup)
        for story in stories:
            link = Wattpad.base_url + story.select_one(".story-card")["href"]
            image = story.select_one(".cover img")["src"]
            title = story.select_one('.story-info .title[aria-hidden="true"]').text.strip()
            stats_values = story.select(".new-story-stats .stats-value")
            read_count = stats_values[0].text if len(stats_values) > 0 else None
            vote_count = stats_values[1].text if len(stats_values) > 1 else None
            chapter_count = stats_values[2].text if len(stats_values) > 2 else None
            description = story.select_one(".description").text.strip()

            results.append({
                "link": link,
                "image": image,
                "title": title,
                "readCount": read_count,
                "voteCount": vote_count,
                "chapterCount": chapter_count,
                "description": description,
            })
        return results
        
@wapegrek.route('')
class Resourcewapen(Resource):
    @wapegrek.doc(params={
        'query': 'Category input romance, anime',
    })
    def get(self):
        """
        Search for Novels from categories 

        Parameters:
        - query: Category input romance, anime, and others (required)
        """
        
        query = request.args.get('query')

        if not query:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'query' diperlukan."})

        try:
             wattpad = Wattpad()
             results = wattpad.search(query)
             return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'result':  results
             })
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

import requests
import base64

def bratg(text):
    """
    Fungsi untuk mengambil gambar dari API dan mengembalikannya dalam format Base64.

    Args:
        text (str): Teks yang akan dimasukkan ke dalam API.

    Returns:
        str: Gambar yang dikodekan dalam Base64, atau pesan kesalahan.
    """
    try:
        # API endpoint
        url = "https://api.ryzendesu.vip/api/sticker/brat"
        params = {"text": text}

        # Step 1: Fetch the image from the API
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # Step 2: Encode the image content in Base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return image_base64
        else:
            return f"Error: Failed to fetch the image. Status code: {response.status_code}"
    
    except Exception as e:
        return f"Error: {str(e)}"
        
@bratgrek.route('')
class Resourcebrat(Resource):
    @bratgrek.doc(params={
        'text': 'Input Text',
    })
    def get(self):
        """
        text to img brat

        Parameters:
        - text: input text (required)
        """
        query = request.args.get('text')

        if not query:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'text' diperlukan."})

        try:
            # Memanggil API eksternal
            api_url = f"https://btch.us.kg/brat?text={query}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                # Mengembalikan gambar langsung dari data biner
                return Response(response.content, content_type="image/png")
            else:
                return jsonify({"creator": "AmmarBN", "status": False, "error": f"Error from external API: {response.status_code}"})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})
            
def upcoming():
    try:
        response = requests.get('https://www.teater.co/upcoming')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        upcoming_films = []
        film_list = soup.select('#filmListResult li')

        for film in film_list:
            title = film.select_one('h3').get_text(strip=True)
            link = film.select_one('a')['href']
            image = film.select_one('img')['src']
            upcoming_films.append({
                'title': title,
                'link': link,
                'image': image
            })

        return upcoming_films
    except Exception as e:
        print(f'Error fetching data: {e}')
        return {
            'success': False,
            'error': str(e)
        }


@theatergrek.route('')
class Resourcetheater(Resource):
    def get(self):
        """
        List theater upcoming

        Parameters:
        - none
        """
        try:
             results = upcoming()
             return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'result':  results
             })
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

@glimggrek.route('')
class Resourcegimg(Resource):
    @glimggrek.doc(params={
        'text': 'Input Text',
    })
    def get(self):
        """
        Search img google

        Parameters:
        - text: input text (required)
        """
        
        query = request.args.get('text')

        if not query:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'text' diperlukan."})

        try:
             url = "https://btch.us.kg/googleimage"
             # Query parameters
             params = {
                 "query": query
             }
             # Sending GET request
             list = []
             response = requests.get(url, params=params).json()
             return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'result':  response["result"]
             })
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})
