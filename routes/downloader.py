import requests, re, json, os, base64, urllib.parse
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
ytdl_bp = Blueprint('youtubedl', __name__)

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
ytdlrek = Namespace('downloader', description='Downloader Api')

# Model untuk response user agents
# user_agent_model = api.model('Downloader', {
#    'user_agents': fields.List(fields.String, description='List of generated User-Agents'),
#    'pembuat': fields.String(description='Creator information')
#})

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
            
        headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': '_ga=GA1.1.6364207.1717837319; __gads=ID=00bce85d94f977a3:T=1717837319:RT=1717839979:S=ALNI_MZDAjs_SNl6GQkU4whEOmcDoVkTwg; __gpi=UID=00000e443e647ee2:T=1717837319:RT=1717839979:S=ALNI_MYkfsQRA_ZduJ8nwTV9z3eV61pDdg; __eoi=ID=26c8d4ac0c9d33c7:T=1717837319:RT=1717839979:S=AA-AfjYHA7UAR40jPrn-ZJDvTEx_; _ga_30X9VRGZQ4=GS1.1.1717837318.1.1.1717840098.0.0.0; FCNEC=%5B%5B%22AKsRol_uWFsgDh-_YrbPyNvMAQCS2PvIbY1jjqzwVRNTPtBXgL9XFZVjBywWxCCEEuYktubvGuyIdEPMRWTBCOvxbhLDyVGEwq9BgZxUP_cYRUamatpo7OTOJE_ao3dyesMDJLR7IWjz_QZ8_KQu9ETkKGsuc765Ng%3D%3D%22%5D%5D',
    'origin': 'https://lovetik.com',
    'priority': 'u=1, i',
    'referer': 'https://lovetik.com/id',
    'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
        }
            
        data = {
            'query': url
        }
        resp = requests.post('https://lovetik.com/api/ajax/search', headers=headers, data=data)
        try:
            username  = resp.json()['author']
            profile   = resp.json()['author_a']
            fullname  = resp.json()['author_name']
            thumbnail = resp.json()['cover']
            deskripsi = resp.json()['desc']
            url = []
            for i in resp.json()['links']:
                url.append(i)
            mp4 = url[8]['a']
            mp3 = url[9]['a']
            return jsonify(
                {
                    'creator': 'AmmarBN',
                    'result': {
                        'username': username,
                        'profile': profile,
                        'fullname': fullname,
                        'thumb': thumbnail,
                        'desc': deskripsi,
                        'mp4': mp4,
                        'mp3': mp3
                    }
                }
            )
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
        api_url = 'https://tools.revesery.com/ig/server.php'
        headers = {
            'authority': 'tools.revesery.com',
            'accept': '*/*',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '_ga=GA1.1.1992994149.1723390762; _ga_G8KSZGHJ0D=GS1.1.1723396058.2.0.1723396058.0.0.0; __gads=ID=830fc255386ea0d4:T=1723396065:RT=1723396065:S=ALNI_MbZibumPe5BD6LmoK2D5EMetnrzqw; __gpi=UID=00000ebd276ca172:T=1723396065:RT=1723396065:S=ALNI_MZO935TwTeIfoNvEJINF6yagpk8ow; __eoi=ID=786948cbe4acb921:T=1723396065:RT=1723396065:S=AA-AfjZebk0McHOHOg-XmqLUo1pX; FCNEC=%5B%5B%22AKsRol8ZsLieH6oXsM3BD1D7mVRqt6cbxIf6M5HSgMRhTlllICfOtuJbS8v9Bn6CTL0Y-bT2wEsb37hiCdm7Xoof9BPMpT7SjRT7zOs-glJNQX4Tj9u5KOeutZgbmshVJUS2v_17YfofLmf3gob_6hfpSOALck24jA%3D%3D%22%5D%5D',
            'origin': 'https://tools.revesery.com',
            'referer': 'https://tools.revesery.com/ig/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'instagramUrl': url,
        }

        # Lakukan request ke API baru
        response = requests.post(api_url, headers=headers, data=data)
        result = response.json()

        # Ambil URL dari respons API
        urls = []
        if result.get("status") == "picker":
            for item in result.get("picker", []):
                urls.append(item.get("url"))
        elif result.get("status") == "redirect":
            urls.append(result.get("url"))

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
        
        headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    #'cookie': '_ga_ZD1YG9MSQ3=GS1.1.1718548942.1.0.1718548942.0.0.0; _gcl_au=1.1.1186587033.1718548943; stpdOrigin={"origin":"direct"}; _sharedID=ac0f93da-c23d-47e8-8463-742b93c505d6; _sharedID_cst=zix7LPQsHA%3D%3D; cto_bidid=y2-ZQV9JYTdKOVhDbU5hWnhjRng0SzNtb3pmS283Q3o0cXRUUG85U1ZmQUI0Wkw1OGZWQkpDaHJJdFN4NHMyR3M2bE10UUdoJTJCdEJydUpyOGZDU3FIdHY5SFd3JTNEJTNE; _cc_id=ac8d725d2061a8118abac3156abc7614; panoramaId_expiry=1718635367072; __gads=ID=3d4f3d41c0f344db:T=1718548967:RT=1718548967:S=ALNI_MYabpBjSDmxnkz_AzqFWLzYd3KBoA; __gpi=UID=00000e4f7116c6b3:T=1718548967:RT=1718548967:S=ALNI_MYXZTJ8sz_K-qnfsDFfuGm9KGgzcg; __eoi=ID=1a5112c16d3c0ed4:T=1718548967:RT=1718548967:S=AA-AfjbSbU0ht3H-gIudkb1x2pCV; _au_1d=AU1D-0100-001718548969-W0J9KTKH-916F; _ga=GA1.2.1010614677.1718548943; _gid=GA1.2.273983052.1718548972; cto_bundle=IGTbU185aGo0SERZSW4lMkJjUW1iSmtMdkRPaVI2VlF1QlRmNzclMkI3TkpXQ2klMkZDN0olMkJ5SXM3WXdJYTh4T2l6TG1Hc0ZabEtybWhvViUyQjRqZVFRSUpqRlpBNUQlMkJ5U1FlbXVUQVhSZ2clMkZyRkpBVVhyOHdRTDNzZGVwZlVDb3gxZXhYYVduVG1q',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers).text
        pattern = r"window\.atob\('([^']+)'\)"
        match = re.search(pattern, response)
        if match:
            base64_string = match.group(1)  # Mengambil nilai yang terdapat dalam tanda kurung tunggal
            decoded_bytes = base64.b64decode(base64_string)  # Mendekode string dari base64
            encoded_string = decoded_bytes.decode('utf-8')  # Mengubah bytes menjadi string UTF-8
            # Dekode URL encoding
            decoded_string = urllib.parse.unquote(encoded_string)
            # Parse JSON ke dalam bentuk dictionary
            data = json.loads(decoded_string)
            username = data['postInfo']['userUsername']
            title = data['postInfo']['title']
            postid = data['postInfo']['postID']
            userid = data['postInfo']['userID']
            totalcomment = data['postInfo']['totalComments']
            createtime = data['postInfo']['createTime']
            data_url = data['postInfo']['media']
            
            return jsonify(
                {
                    'creator': 'AmmarBN',
                    'status': True,
                    'result': {
                        'a_username': username,
                        'b_title': title,
                        'c_postid': postid,'d_userid': userid,
                        'e_totalcomment': totalcomment,
                        'f_create': createtime,
                        'g_url': f'https://cache.lahelu.com/{data_url}'
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
        
@ytdlrek.route('')
class DownloadytResource(Resource):
    @ytdlrek.doc(params={
        'url': 'Url YouTube',
        'apikey': 'API Key for authentication'
    })
    def get(self):
        """
        Downloader YouTube Video & Audio.

        Parameters:
        - url: Url YouTube (required)
        - apikey: API Key for authentication (required)
        """
        url = request.args.get('url')
        apikey = request.args.get('apikey')
        
        if not url:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'url' diperlukan."}), 400
        
        if not apikey:
            return jsonify({"creator": "AmmarBN", "error": "Parameter 'apikey' diperlukan."}), 400
        
        # Read existing users data
        limit_error = check_and_update_request_limit(apikey)
        if limit_error:
            return jsonify(limit_error[0]), limit_error[1]

        # Request to the API
        api_url = f'https://api.betabotz.eu.org/api/download/allin?url={url}&apikey=Hoshiyuki'
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise HTTPError for bad responses

            data = response.json()
            if not data.get('status'):
                return jsonify({"creator": "AmmarBN", "error": "Failed to fetch data from API."}), 500

            result = data.get('result')
            title = result.get('title')
            thumbnail = result.get('thumbnail')
            duration = result.get('duration')
            medias = result.get('medias')

            mp4_url = None
            mp3_url = None

            for media in medias:
                if media.get('extension') == 'mp4':
                    mp4_url = media.get('url')
                elif media.get('extension') == 'mp3':
                    mp3_url = media.get('url')

            if not mp4_url and not mp3_url:
                return jsonify({"creator": "AmmarBN", "error": "No valid media URLs found in API response."}), 500

            # Fetch additional details using pytube
            yt = YouTube(url)
            author = yt.author
            views = yt.views

            return jsonify({
                'creator': 'AmmarBN',
                'status': True,
                'result': {
                    'channel': '@' + author,
                    'title': title,
                    'total_views': views,
                    'duration': duration,
                    'thumbnail': thumbnail,
                    'mp4': mp4_url,
                    'audio': mp3_url
                }
            })

        except requests.exceptions.HTTPError as e:
            return jsonify({"creator": "AmmarBN", "error": f"HTTP error occurred: {str(e)}"}), 500
        
        except requests.exceptions.RequestException as e:
            return jsonify({"creator": "AmmarBN", "error": f"Request failed: {str(e)}"}), 500
        
        except Exception as e:
            return jsonify({"creator": "AmmarBN", "error": f"Failed to fetch video details: {str(e)}"}), 500
