import requests, re, json, os, base64, urllib.parse, time, random
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
spoty_bp = Blueprint('spoty', __name__)
trera_bp = Blueprint('terabox', __name__)
bilibili_bp = Blueprint('bilibili', __name__)
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
spotyrek = Namespace('downloader', description='Downloader Api')
terarek = Namespace('downloader', description='Downloader Api')
bilibilirek = Namespace('downloader', description='Downloader Api')
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
    })
    def get(self):
        """
        Downloader Tiktok No WM.

        Parameters:
        - url: Url Tiktok (required)
        """
        
        url = request.args.get('url')
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

        try:
             resl = tiktok2(url)
             return jsonify({'creator': 'AmmarBN', 'result': {'title': resl['title'], 'cover': resl['cover'], 'origin_cover': resl['origin_cover'], 'no_watermark': resl['no_watermark'], }})
        except requests.exceptions.RequestException as e:
            return jsonify({"creator": "AmmarBN", "error": str(e)})

def find_asu(text):
    # Menemukan semua pola dalam tanda kutip
    matches, code = re.findall(r'(\d+)', text), re.findall(r'"([^"]*)"', text)
    return code[-2], code[-1], matches[-4], matches[-3], matches[-2], matches[-1]
    
def base_convert(d, e, f):
    g = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
    h = g[:e]
    i = g[:f]
    j = 0
    for c, char in enumerate(reversed(d)):
        if char in h:
            j += h.index(char) * (e ** c)
    
    k = ""
    while j > 0:
        k = i[j % f] + k
        j //= f
    
    return k or "0"

def decode(encoded, u, n, t, e, r):
    r = ""
    i = 0
    while i < len(encoded):
        s = ""
        while encoded[i] != n[e]:
            s += encoded[i]
            i += 1
        i += 1  # Move past the separator
        
        for j in range(len(n)):
            s = s.replace(n[j], str(j))
        
        decoded_char = chr(int(base_convert(s, e, 10)) - t)
        r += decoded_char
    
    return r
    
@instagramdlrek.route('')
class DownloadigResource(Resource):
    @instagramdlrek.doc(params={
        'url': 'Instagram URL',
    })
    def get(self):
        url = request.args.get('url')

        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' is required."})


        # Siapkan request ke API baru
        #resp = requests.get(f"https://widipe.com/download/igdl?url={url}")
        #urls = resp.json()["result"][0]["url"]
        
        # api baru
#        headers = {
#            "Host": "saveclip.app",
#            "Cache-Control": "max-age=0",
#            "Upgrade-Insecure-Requests": "1",
#            "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
#            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#            "Sec-Fetch-Site": "none",
#            "Sec-Fetch-Mode": "navigate",
#            "Sec-Fetch-User": "?1",
#            "Sec-Fetch-Dest": "document",
#            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
#        }

#        token = requests.get("https://saveclip.app/en", headers=headers)
#        cs = re.search(',k_exp="(.*?)",k_token="(.*?)"', token.text)
#        headers = {
#            "Host": "v3.saveclip.app",
#            "Content-Length": "194",
#            "Accept": "*/*",
#            "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
#            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#            "Origin": "https://saveclip.app",
#            "Sec-Fetch-Site": "same-site",
#            "Sec-Fetch-Mode": "cors",
#            "Sec-Fetch-Dest": "empty",
#            "Referer": "https://saveclip.app/",
#    "Accept-Encoding": "gzip, deflate, br",
#            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
#        }

# Data payload
#        data = {
#            "k_exp": cs.group(1),
#            "k_token": cs.group(2),
#            "q": url,
#            "t": "media",
#            "lang": "en",
#            "v": "v2",
#        }
#        res = requests.post("https://v3.saveclip.app/api/ajaxSearch", headers=headers, data=data)
#        encoded_string, code_string, c1, c2, c3, c4 = find_asu(urllib.parse.unquote(res.json()["data"]))
#        decoded_result = decode(str(encoded_string), int(c1),f"{code_string}",int(c2),int(c3),int(c4))
#        inner_html_match = re.search(r'innerHTML = "(.*?)";', decoded_result)
#        decoded_url = urllib.parse.unquote(inner_html_match.group(1))
#        code_html = parser(decoded_url, "html.parser")
#        list = ([a.get("href") for a in code_html.find_all("a")])
#        url_t, url_d = list[0], list[1]
#        url_rt = (url_t.replace('"', '').replace("\\", ""))
#        url_rd = (url_d.replace('"', '').replace("\\", ""))
        params = {"url": url}
        headers = {"accept": "application/json"}
        url_rd = requests.get("https://api.tioo.eu.org/download/igdl", headers=headers, params=params).json()["result"][0]["url"]
        return jsonify({
            "creator": "AmmarBN",
            "result": url_rd,
            "status": True
        })
        
@twitterdlrek.route('')
class DownloadtwResource(Resource):
    @twitterdlrek.doc(params={
        'url': 'Url Twitter',
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Twitter Video.

        Parameters:
        - url: Url twitter (required)
        """
        url = request.args.get('url')

        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

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
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Facebook Video.

        Parameters:
        - url: Url Facebook (required)
        """
        url = request.args.get('url')

        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})
        
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
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Mediafire File.

        Parameters:
        - url: Url Mediafire (required)
        """
        
        url = request.args.get('url')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

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
                'results': {'NamaFile': name, 'SizeFile': size, 'Upload': upload, 'Download': media}
            }
        )

@pinterestviddlrek.route('')
class DownloadPinVidResource(Resource):
    @pinterestviddlrek.doc(params={
        'url': 'Url Pinterest Video',
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Pinterest Video.

        Parameters:
        - url: Url Pinterest Video (required)
        """
        
        url = request.args.get('url')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

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
    })
    # @api.marshal_with(user_agent_model)
    def get(self):
        """
        Downloader Lahelu Post.

        Parameters:
        - url: Url Lahellu Post (required)
        """
        
        url = request.args.get('url')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."})

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

def ytmp3andmp4(youtube_url, format="mp4", audio_bitrate="128", video_quality="720", v_codec="h264"):
    """
    Convert YouTube video to MP3 or MP4 format.

    Args:
        youtube_url (str): The URL of the YouTube video.
        format (str): Desired format ("mp3" or "mp4"). Default is "mp4".
        audio_bitrate (str): Bitrate for audio. Default is "128".
        video_quality (str): Quality of the video. Default is "720".
        v_codec (str): Video codec. Default is "h264".
    
    Returns:
        dict: Response from the API containing the download link or error message.
    """
    # Step 1: Fetch the API key
    headers = {
        "Host": "api.mp3youtube.cc",
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://iframe.y2meta-uk.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://iframe.y2meta-uk.com/",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "If-None-Match": 'W/"7e-3ZPGIytlLAa5LUUpFaSY1bbvtTU-gzip"'
    }
    response = requests.get("https://api.mp3youtube.cc/v2/sanity/key", headers=headers)
    key = response.json().get("key", None)
    
    if not key:
        return None

    headers.update({
        "Key": key,
        "Content-Type": "application/x-www-form-urlencoded"
    })
    data = {
        "link": youtube_url,
        "format": format,
        "audioBitrate": audio_bitrate,
        "videoQuality": video_quality,
        "vCodec": v_codec
    }
    conv_response = requests.post("https://api.mp3youtube.cc/v2/converter", headers=headers, data=data)
    
    if conv_response.status_code == 200:
        return conv_response.json()
    else:
        return None

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
            resl = ytmp3andmp4(url, format="mp4")
            return jsonify({'creator': 'AmmarBN','status': True,'result': resl.get("url")})
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
            resl = ytmp3andmp4(url, format="mp3")
            return jsonify({'creator': 'AmmarBN','status': True,'result': resl.get("url")})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

@spotyrek.route('')
class DownloadspotyResource(Resource):
    @spotyrek.doc(params={
        'url': 'Url Spotify'
    })
    def get(self):
        """
        Downloader Spotify Audio.

        Parameters:
        - url: Url Spotify (required)
        """
        url = request.args.get('url')
        
        # Parameter validation
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."}), 400

        try:
            urls = "https://spotify-down.com/api/metadata"
            params = {
                "link": url
            }

            headers = {
                "Host": "spotify-down.com",
                "Content-Length": "0",
                "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Origin": "https://spotify-down.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://spotify-down.com/",
            #    "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": "_ga_NPMTFQ207N=GS1.1.1733203589.1.0.1733203589.0.0.0; _ga=GA1.1.1034080416.1733203590; __gads=ID=334f15667f202da8:T=1733203592:RT=1733203592:S=ALNI_MaT4xYx0hxE9JjQnKqETVI4uKjjRg; __gpi=UID=00000f7e8c8134cf:T=1733203592:RT=1733203592:S=ALNI_MaSe9q5GGXgr49kmsNdFcR8LRD7RQ; __eoi=ID=5b772c3430346844:T=1733203592:RT=1733203592:S=AA-AfjZ9Hq1Y2iHwfAhsVE_RShau"
            }

            res = requests.post(urls, headers=headers, params=params, data="")
            urlss = "https://spotify-down.com/api/download"
            params = {
                "link": res.json()["data"]["link"],
                "n": res.json()["data"]["title"],
                "a": res.json()["data"]["artists"]
            }

            headers = {
                "Host": "spotify-down.com",
                "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
                "Accept": "*/*",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://spotify-down.com/",
            #    "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": "_ga=GA1.1.1034080416.1733203590; __gads=ID=334f15667f202da8:T=1733203592:RT=1733203592:S=ALNI_MaT4xYx0hxE9JjQnKqETVI4uKjjRg; __gpi=UID=00000f7e8c8134cf:T=1733203592:RT=1733203592:S=ALNI_MaSe9q5GGXgr49kmsNdFcR8LRD7RQ; __eoi=ID=5b772c3430346844:T=1733203592:RT=1733203592:S=AA-AfjZ9Hq1Y2iHwfAhsVE_RShau; _ga_NPMTFQ207N=GS1.1.1733203589.1.1.1733203615.0.0.0"
            }

            resp = requests.get(urlss, headers=headers, params=params)
            if resp.json()["data"]["success"] == True:
               return jsonify({'creator': 'AmmarBN','status': True,'result': resp.json()["data"]["link"]})
            else:return jsonify({'status': False, 'msg': f'url not found '})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

def terabox(url):
    try:
        # Step 1: Get the file list
        response = requests.post('https://teradl-api.dapuntaratya.com/generate_file', json={'mode': 1, 'url': url})
        response.raise_for_status()
        data = response.json()
        
        file_list = data.get('list', [])
        js_token = data['js_token']
        cookie = data['cookie']
        sign = data['sign']
        timestamp = data['timestamp']
        shareid = data['shareid']
        uk = data['uk']
        
        result = []
        
        # Step 2: Generate download links for each file
        for file in file_list:
            try:
                payload = {
                    'js_token': js_token,
                    'cookie': cookie,
                    'sign': sign,
                    'timestamp': timestamp,
                    'shareid': shareid,
                    'uk': uk,
                    'fs_id': file['fs_id']
                }
                dl_response = requests.post('https://teradl-api.dapuntaratya.com/generate_link', json=payload)
                dl_response.raise_for_status()
                dl_data = dl_response.json()
                
                if 'download_link' in dl_data:
                    result.append({
                        'fileName': file['name'],
                        'type': file['type'],
                        'thumb': file.get('image'),
                        'url': dl_data['download_link']['url_1']
                    })
            except Exception as e:
                return (f"Failed to generate link for file {file['name']}: {e}")
        
        return result
    except Exception as e:
        return []


@terarek.route('')
class DownloadteraboxResource(Resource):
    @terarek.doc(params={
        'url': 'Url Terabox'
    })
    def get(self):
        """
        Downloader Terabox.

        Parameters:
        - url: Url Terabox (required)
        """
        url = request.args.get('url')
        
        # Parameter validation
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."}), 400

        try:
            list = []
            files = terabox(url)
            for file in files:
                list.append(file)
            if list:
               return jsonify({'creator': 'AmmarBN','status': True,'result': list})
            else:return jsonify({'status': False, 'msg': f'url not found '})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

def calculate_duration(duration_seconds):
    hours = duration_seconds // 3600  # Hitung jam
    minutes = (duration_seconds % 3600) // 60  # Hitung menit
    seconds = duration_seconds % 60  # Hitung detik

    return f"{hours:02}:{minutes:02}:{seconds:02}"
    
@bilibilirek.route('')
class DownloadbilibiliResource(Resource):
    @bilibilirek.doc(params={
        'url': 'Url bilibili'
    })
    def get(self):
        """
        Downloader bilibili.

        Parameters:
        - url: Url bilibili (required)
        """
        url = request.args.get('url')
        
        # Parameter validation
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."}), 400

        try:
            proxies = [
                "199.195.253.141:1080",
                "72.10.164.178:1417",
                "63.35.64.177:3128",
                "13.37.73.214:3128",
                "13.37.89.201:3128",
                "54.152.3.36:80",
                "13.208.56.180:80",
                "160.86.242.238:80"
            ]
            random_proxy = random.choice(proxies)
            proxy = {
                "http": f"http://{random_proxy}",
                #"https": f"https://{random_proxy}",
            }
            #title = re.search("<title>(.*?)</title>", requests.get(url, proxies=proxy).text).group(1)
            match = re.search(r'/video/(\d+)', url)
            if match:
                 video_id = match.group(1)
                 params = {
                     "s_locale": "en_US",
                     "platform": "html5_a",
                     "aid": video_id,
                     "qn": "64",
                     "type": "0",
                     "device": "wap",
                     "tf": "0",
                     "spm_id": "bstar-web.ugc-video-detail.0.0",
                     "from_spm_id": ""
                 }

                 headers = {
                     "authority": "api.bilibili.tv",
                     "accept": "application/json, text/plain, */*",
                     "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                     "cookie": "buvid3=5d7ab82a-30aa-4f72-91be-fa0ef656a34864680infoc; bstar-web-lang=id; _ga=GA1.1.1172665079.1733307593; _ga_X4BG3JXFB1=GS1.1.1733307593.1.1.1733307615.0.0.0",
                     "origin": "https://www.bilibili.tv",
                     "referer": url,
                     "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
                     "sec-ch-ua-mobile": "?1",
                     "sec-ch-ua-platform": '"Android"',
                     "sec-fetch-dest": "empty",
                     "sec-fetch-mode": "cors",
                     "sec-fetch-site": "same-site",
                     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                 }
                 array_video = []
                 resp = requests.get("https://api.bilibili.tv/intl/gateway/web/playurl", params=params, proxies=proxy)
                 return jsonify({'creator': 'AmmarBN','status': True,'result': [resp.json()]})
                 for video in resp.json()['data']['playurl']['video']:
                     array_video.append({
                       # "title": title,
                        "url": video['video_resource']['url'],
                        "url_backup": video['video_resource']['backup_url'][0],
                        "quality": video['stream_info']['desc_words'],
                        "duration": calculate_duration(video['video_resource']['duration']),
                        "mime_type": video['video_resource']['mime_type'],
                     })
                 return jsonify({'creator': 'AmmarBN','status': True,'result': array_video})
            else:return jsonify({'status': False, 'msg': f'url not found '})
        except Exception as e:
            return jsonify({'status': False, 'msg': f'Error: {str(e)}'})

