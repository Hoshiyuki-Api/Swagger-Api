import requests, re, json, os, base64, urllib.parse
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as parser
from flask import Blueprint, jsonify, request
from datetime import datetime

ckphone_bp = Blueprint('amsus', __name__)
cknik_bp = Blueprint('cknik', __name__)
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

@ckphone_bp.route('/leakphone', methods=['GET'])
def leakphone():
    nomor = request.args.get('nomor')
    apikey = request.args.get('apikey')

    if not nomor:
        return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})

    if not apikey:
        return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})

    limit_error = check_and_update_request_limit(apikey)
    if limit_error:
        return jsonify(limit_error[0]), limit_error[1]
    try:
        response = requests.post(
            'https://leakosintapi.com/',
            json = {
                'token': "7274295636:7nrgvRi9",
                'request': nomor,
                'limit': 100,
                'lang': 'id'
            }
        ).json()
        formatted_response = json.dumps(response, indent=2, ensure_ascii=False)
        passport = response['List']['KomInfo Indonesia']['Data'][0]['Passport']
        return jsonify({
            'result': passport
        })
    except requests.exceptions.RequestException as e:return jsonify({'error': str(e)})

def GetCode(passport, formatted_phone):
  url = "https://cekdptonline.kpu.go.id/v2"
  headers = {
      "Host": "cekdptonline.kpu.go.id",
      "Connection": "keep-alive",
      "Content-Length": "2059",
      "Accept": "application/json, text/plain, */*",
      "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
      "Content-Type": "application/json;charset=UTF-8",
      "Origin": "https://cekdptonline.kpu.go.id",
      "Sec-Fetch-Site": "same-origin",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Dest": "empty",
      "Referer": "https://cekdptonline.kpu.go.id/",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
      "Cookie": "_ga=GA1.3.898975063.1723632644; aliyungf_tc=f5298cbe2a7209647b3b4a631ce40a48a666a2ba1bfe21ac2d474f295fa35d7a; acw_tc=ac11000117257210620496016e8bd8776c0c4d4f8ce19c9d41eaa1c0becf7d; _gid=GA1.3.1584439243.1725721063"
  }
  data = {
      "query": """
      {
        findNikPilkada (
            nik: "%s",
            wilayah_id:0,
            hp: "%s"
            token:"qs1byəL03AFcWeAxJP5ʍ_Lu3ɴ3WugztD9HVT7fMʌaMilfL6iOɢRpw2CgOlXJZCDZk32jCR-yc8Xu39lz0ZFtZhUg9O5DYrVkSdyDWIbWK2gkqnUk4NrYNQdvDr79vt0wU1Q2if866Crr5Lj4hmgvVSLiuopX3Hu7BGrJ3gqhIQHsrJpzzBxndtu-NlQhD1_Rm0iWyooVuqVXHJEsKNxNwiDPMMR1EjnXYgg6IYa3hnDMpBYQjIoMkhOkihPnFcD_80pupLcF9-uqKMiZLVkI76PqxRelZiVzpIf1tx4Tz_9KRESf4DKQvj24ixzNO3iiv6nVEV3lCfLKyjaj5LYO6XnqaRMgObDGfhtTD4C9zHgf60q3dBW8dafiOf7nqeQ0MUa8V4i-oJlkaPOwr9jalZf1-7I0B00vOmB4pUHRobGgCwsF1w_U7fAFkge3pDWPdNP1DPX29xR7BvYo0b9baNPA_b2JTBUHUGM9UjgQY0DtOlEkG-hapUnJW2icmpE4kw6ikpkOn8Ye4syT-slKJSrx4nJL4F6KTj9rlrBaMa_ItbJknHDUiQLbjamOWSSstZYLTs8VVJsUE9RnO40X2Qei9n0ttFKAgh_9r-WLpXfLdM0CqR9VQ1fH5RkFSRqQxYV8lOVRmh3Ek5jiXfHpSTuCZcD-F0g51zPqP4KGcjUtCGLdllW18xtoehdPnrccD9sCuSmIs5wXL0F39Ai9p9XmcjI3ZuRjnU-MD64t7d4X2UVZDJatKSTFnkU5Yy5qX9_HNyx1fhC0BowKVCN_Bo9RBwnt6mu3yJ0rb0ySUCiQD-mq7nf_-0GoOPSsMiv2FdcPnog8pSVjgq___CMTk1qOPwRH3ZuAEsy0uOsJf1JODaCB14QoG7j5qoMLvHTFskuoCb6i4DMvLfLh4",
        ) {
          nama,
          nik,
          nkk,
          provinsi,
          kabupaten,
          kecamatan,
          kelurahan,
          tps,
          alamat,
          lat,
          lon,
          metode,
          lhp {
                nama,
                nik,
                nkk,
                kecamatan,
                kelurahan,
                tps,
                id,
                flag,
                source,
                alamat,
                lat,
                lon,
                metode
          }
        }
      }
      """ % (passport, formatted_phone)
  }

  return requests.post(url, headers=headers, json=data).json()['errors'][0]['message']

@cknik_bp.route('/cknik', methods=['GET'])
def checknik():
    nik = request.args.get('nik')
    nomor = request.args.get('nomor')
#    hash = request.args.get('hash')
 #   code = request.args.get('code')
    apikey = request.args.get('apikey')

    if not nik:
    	return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})
    
    if not nomor:
        return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})

    if not apikey:
        return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})

    limit_error = check_and_update_request_limit(apikey)
    if limit_error:
        return jsonify(limit_error[0]), limit_error[1]
#    try:
#        if len(hash) > 0:
#            if not code:
#               return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})
#        else:
    hash_code = GetCode(nik, nomor)
    return jsonify({"creator": "AmmarBN", "result": hash_code})
#    except requests.exceptions.RequestException as e:return jsonify({'error': str(e)})
