import requests, re, json, os, base64, urllib.parse, time
from pytube import YouTube
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as parser
from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_restx import Namespace, Resource, fields

tiktok_bp = Blueprint('tiktokdl', __name__)
igdl_bp = Blueprint('igdl', __name__)
twitter_bp = Blueprint('twitter', __name__)
facebook_bp = Blueprint('facebook', __name__)
mediafire_bp = Blueprint('mediafir', __name__)
pinterestvid_bp = Blueprint('pinterestvid', __name__)#
laheludl_bp = Blueprint('lahelu', __name__)
ytdlmp4_bp = Blueprint('youtubedl', __name__)
ytdlmp3_bp = Blueprint('youtubedl3', __name__)

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
tiktokdlrek = Namespace('downloader', description='Downloader Api')
instagramdlrek = Namespace('downloader', description='Downloader Api')
twitterdlrek = Namespace('downloader', description='Downloader Api')
facebookdlrek = Namespace('downloader', description='Downloader Api')
mediafiredlrek = Namespace('downloader', description='Downloader Api')
pinterestviddlrek = Namespace('downloader', description='Downloader Api')
laheludlrek = Namespace('downloader', description='Downloader Api')
ytdlmp4rek = Namespace('downloader', description='Downloader Api')
ytdlmp3rek = Namespace('downloader', description='Downloader Api')

# Model untuk response user agents
# user_agent_model = api.model('Downloader', {
#    'user_agents': fields.List(fields.String, description='List of generated User-Agents'),
#    'pembuat': fields.String(description='Creator information')
#})

def tiktok2(query):
    try:
        url = 'https://tikwm.com/api/'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'current_language=en',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36'
        }
        data = {'url': query, 'hd': '1'}
        
        response = requests.post(url, data=data, headers=headers)
        response_data = response.json()['data']
        
        result = {
            'title': response_data['title'],
            'cover': response_data['cover'],
            'origin_cover': response_data['origin_cover'],
            'no_watermark': response_data['play'],
            'watermark': response_data['wmplay'],
            'music': response_data['music']
        }
        return result
    except Exception as error:
        raise error
        
# Endpoint untuk menghasilkan user agents acak
@tiktokdlrek.route('')
class DownloadttResource(Resource):
    @tiktokdlrek.doc(params={
        'url': 'Url Tiktok',
        'apikey': 'API Key for authentication'
    })
    def get(self):
        """
        Downloader Tiktok No WM.

        Parameters:
        - url: Url Tiktok (required)
        - apikey: API Key for authentication (required)
        """
        
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
            
        try:
             resl = tiktok2(url)
             return jsonify({'creator': 'AmmarBN', 'result': {'title': resl['title'], 'cover': resl['cover'], 'origin_cover': resl['origin_cover'], 'no_watermark': resl['no_watermark'], }})
        except requests.exceptions.RequestException as e:
            return jsonify({"creator": "AmmarBN", "error": str(e)})

@instagramdlrek.route('')
class DownloadigResource(Resource):
    @instagramdlrek.doc(params={
        'url': 'Instagram URL',
        'apikey': 'API Key for authentication'
    })
    def get(self):
        url = request.args.get('url')
        apikey = request.args.get('apikey')

        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' is required."})
        
        if not apikey:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' is required."})

        # Periksa dan perbarui batas permintaan
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]

        # Siapkan request ke API baru
        #resp = requests.get(f"https://widipe.com/download/igdl?url={url}")
        #urls = resp.json()["result"][0]["url"]
        
        # api baru
        headers = {'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"','sec-ch-ua-platform': 'Android','Referer': 'https://instasave.website/','sec-ch-ua-mobile': '?1','User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36','Content-Type': 'application/x-www-form-urlencoded',}
        data = {'url': url}
        html_content = requests.post('https://api.instasave.website/media', headers=headers, data=data).text
        inner_html_match = re.search(r'innerHTML\s*=\s*"(.*?)";', html_content, re.DOTALL)
        if inner_html_match:
        	extracted_html = inner_html_match.group(1)
        	thumb_url = re.search('"https://cdn.instasave.website/(.*?)"', extracted_html)
        	link_vido = thumb_url.group(1)
        	urls = "https://cdn.instasave.website/{}".format(link_vido.replace("\\", ""))
        else:urls = None
        return jsonify({
            "creator": "AmmarBN",
            "result": urls,
            "status": True
        })
        
@twitterdlrek.route('')
class DownloadtwResource(Resource):
    @twitterdlrek.doc(params={
        'url': 'Url Twitter',
        'apikey': 'API Key for authentication'
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Twitter Video.

        Parameters:
        - url: Url twitter (required)
        - apikey: API Key for authentication (required)
        """
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
        try:
            data = {'URL': url}
            req = requests.post('https://twdown.net/download.php',data=data).text
            kl_vd = req.split('download href="')[2];
            id_vid = kl_vd.split('"')[0];
            return jsonify(
                {
                    'creator': 'AmmarBN',
                    'status': True,
                    'result': {
                        'url': id_vid
                    }
                }
            )
        except requests.exceptions.RequestException as e:
            return jsonify(
                {
                    'creator': 'AmmarBN',
                    'result': 'error',
                    'status': False
                    }
            )
        
@facebookdlrek.route('')
class DownloadfbResource(Resource):
    @facebookdlrek.doc(params={
        'url': 'Url Facebook',
        'apikey': 'API Key for authentication'
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Facebook Video.

        Parameters:
        - url: Url Facebook (required)
        - apikey: API Key for authentication (required)
        """
        url = request.args.get('url')
        apikey = request.args.get('apikey')
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        limit_error = check_and_update_request_limit(apikey)
        
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]
        
        try:
            api = requests.get(f'https://aemt.me/download/fbdl?url={url}')
            res = api.json()
            if res.get('status'):
                normal = res.get('result', {}).get('Normal_video')
                high = res.get('result', {}).get('HD')
                audio = res.get('result', {}).get('audio')
                if normal or high or audio:
                    return jsonify(
                        {
                            'creator': 'AmmarBN',
                            'status': True,
                            'result': {
                                'normal': normal,
                                'high_vid': high,
                                'audio': audio
                            }
                        }
                    )
                else:
                    return jsonify({"creator": "AmmarBN", "error": "Gagal memproses permintaan ke API."}), 500
            else:
                return jsonify({"creator": "AmmarBN", "error": "Gagal memproses permintaan ke API."}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"creator": "AmmarBN", "error": str(e)}), 500
    
@mediafiredlrek.route('')
class DownloadmediafireResource(Resource):
    @mediafiredlrek.doc(params={
        'url': 'Url Mediafire',
        'apikey': 'API Key for authentication'
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Mediafire File.

        Parameters:
        - url: Url Mediafire (required)
        - apikey: API Key for authentication (required)
        """
        
        url = request.args.get('url')
        apikey = request.args.get('apikey')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        limit_error = check_and_update_request_limit(apikey)
        
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]
        
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        type = soup.find('div', {'class': 'filename'}).text.strip()
        name = soup.find('div', {'class': 'dl-btn-label'}).text.strip()
        
        for b in soup.find_all('ul', {'class':'details'}):
            size   = re.search('<li>File size: <span>(.*?)</span></li>', str(b)).group(1)
            upload = re.search('<li>Uploaded: <span>(.*?)</span></li>', str(b)).group(1)
            
        media = soup.find('a', {'class': 'input popsok'}).get('href')
        return jsonify(
            {
                'creator': 'AmmarBN',
                'status': True,
                'url': media
            }
        )

@pinterestviddlrek.route('')
class DownloadPinVidResource(Resource):
    @pinterestviddlrek.doc(params={
        'url': 'Url Pinterest Video',
        'apikey': 'API Key for authentication'
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Pinterest Video.

        Parameters:
        - url: Url Pinterest Video (required)
        - apikey: API Key for authentication (required)
        """
        
        url = request.args.get('url')
        apikey = request.args.get('apikey')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
            
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
            
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]
            
        c = requests.post('https://pinterestvideodownloader.com/download.php',
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "_ga_966QNV4G77=GS1.1.1718265709.1.1.1718265710.0.0.0; _ga=GA1.2.431955486.1718265710; _gid=GA1.2.1691914427.1718265710; __gads=ID=a768755ea54ad065:T=1718265744:RT=1718265744:S=ALNI_MYhy1D7j7Sk-L38lY0gCrvHslkj9w; __gpi=UID=00000e4a44effcb5:T=1718265744:RT=1718265744:S=ALNI_MYlyVI3dB_rxdfiktijz5hqjdFh3A; __eoi=ID=bcaa659e3f755205:T=1718265744:RT=1718265744:S=AA-AfjaNqVe1HORKDn3EorxJl5TE; FCNEC=%5B%5B%22AKsRol-DFkw9G-FS4szSzz5S-Zy-awxxF02UE3axThxkDqbMdR-KD0ss2AkukIaNNXn-fXts6XPmkNEPhKLEh-MWatFyvpof-XZuWVyQDQIAatU_iGwEIPl3TYlsnsZdyNvsNGsr0w0yz2xNc-o7rSwnGm5sWti7ag%3D%3D%22%5D%5D",
            "Origin": "https://pinterestvideodownloader.com",
            "Referer": "https://pinterestvideodownloader.com/id/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            },
        data={
            "url": url
        }
        ).text
        d = re.search('<video style="width: 100%;height:450px;" src="(.*?)" controls autoplay>', str(c)).group(1)
        return jsonify(
            {
                'creator': 'AmmarBN',
                'status': True,
                'result': d
            }
        )
    
@laheludlrek.route('')
class DownloadlaheluResource(Resource):
    @laheludlrek.doc(params={
        'url': 'Url Lahelu',
        'apikey': 'API Key for authentication'
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Lahelu Post.

        Parameters:
        - url: Url Lahellu Post (required)
        - apikey: API Key for authentication (required)
        """
        
        url = request.args.get('url')
        apikey = request.args.get('apikey')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
        
        if apikey is None:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."})
        
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]

        params = {"postID": url.replace("https://lahelu.com/post/", "")}
        headers = {"Host": "lahelu.com","accept": "application/json, text/plain, /","user-agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7","cookie": "_ga=GA1.1.1763889101.1729515843; _gcl_au=1.1.1664196277.1729515843; _ga_ZD1YG9MSQ3=GS1.1.1729571966.2.1.1729573139.56.0.175494160","if-none-match": 'W/"257-Brv/UpPGmYCjDMihALxbhOUJX6s"'}
        response = requests.get("https://lahelu.com/api/post/get", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            post_info = data.get("postInfo", {})
            post_id = post_info.get("postID", "")
            user_id = post_info.get("userID", "")
            title = post_info.get("title", "")
            media = post_info.get("media", "")
            sensitive = post_info.get("sensitive", False)
            hashtags = post_info.get("hashtags", [])
            create_time = post_info.get("createTime", 0)
            
            return jsonify(
                {
                    'creator': 'AmmarBN',
                    'status': True,
                    'result': {
                        'user_id': user_id,
                        'post_id': post_id,
                        'post_info': post_info,
                        'title': title,
                        'media': media,
                        'sensitive': sensitive,
                        'hashtags': hashtags,
                        'create_time': create_time
                        }
                }
            )
        else:
            return jsonify(
                {
                    'creator': 'AmmarBN',
                    'status': False,
                    'result': {}
                }
            )


class Ddownr:
    @staticmethod
    def download(url, format, max_retries=10):
        try:
            response = requests.get(
                f"https://p.oceansaver.in/ajax/download.php?copyright=0&format={format}&url={url}",
                headers={
                    'User-Agent': 'MyApp/1.0',
                    'Referer': 'https://ddownr.com/enW7/youtube-video-downloader'
                }
            )
            data = response.json()
            media = Ddownr.cek_progress(data['id'], max_retries)
            return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'format': format,
                'title': data['title'],
                'thumbnail': data['info']['image'],
                'downloadUrl': media
            })
        except requests.RequestException as error:
            return jsonify({
                'success': False,
                'message': str(error)
            })

    @staticmethod
    def cek_progress(id, max_retries):
        retries = 0
        try:
            while retries < max_retries:
                progress_response = requests.get(
                    f"https://p.oceansaver.in/ajax/progress.php?id={id}",
                    headers={
                        'User-Agent': 'MyApp/1.0',
                        'Referer': 'https://ddownr.com/enW7/youtube-video-downloader'
                    }
                )
                data = progress_response.json()
                if data['progress'] == 1000:
                    return data['download_url']
                else:
                    time.sleep(1)
                    retries += 1
            return jsonify({
                'success': False,
                'message': 'Exceeded max retries without completion'
            })
        except requests.RequestException as error:
            return jsonify({
                'success': False,
                'message': str(error)
            })
        
@ytdlmp4rek.route('')
class DownloadytResource(Resource):
    @ytdlmp4rek.doc(params={
        'url': 'Url YouTube'
    })
    def get(self):
        """
        Downloader YouTube Video.

        Parameters:
        - url: Url YouTube (required)
        """
        url = request.args.get('url')
        
        # Parameter validation
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."}), 400

        try:
            ddownr = Ddownr()
            res = ddownr.download(url, "720")
        #    return jsonify({res})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})
            
@ytdlmp3rek.route('')
class Downloadytmp3Resource(Resource):
    @ytdlmp3rek.doc(params={
        'url': 'Url YouTube'
    })
    def get(self):
        """
        Downloader YouTube Audio.

        Parameters:
        - url: Url YouTube (required)
        """
        url = request.args.get('url')
        
        # Parameter validation
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."}), 400

        try:
            ddownr = Ddownr()
            res = ddownr.download(url, "mp3")
         #   return jsonify({res})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})
