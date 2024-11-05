import requests, re, json, os, base64, urllib.parse, time
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as parser
from flask import Blueprint, jsonify, request
from datetime import datetime

ckphone_bp = Blueprint('amsus', __name__)
cknik_bp = Blueprint('cknik', __name__)
ckwalet_bp = Blueprint('ckwalet', __name__)
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
        if nomor in ["6288229683561","6287708773367","6283139844517"]:
            return jsonify({"result": "Hayo mau leak owner, dikasi pitur malah mau nge dox owner", "status": True})
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
            'result': response,
            "status": True
        })
    except requests.exceptions.RequestException as e:return jsonify({'error': str(e)})

@cknik_bp.route('/cknik', methods=['GET'])
def checknik():
    nik = request.args.get('nik')
    apikey = request.args.get('apikey')

    if not nik:
    	return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})

    if not apikey:
        return jsonify({"creator": "AmmarBN", "error": "tidak ada parameter"})

    limit_error = check_and_update_request_limit(apikey)
    if limit_error:
        return jsonify(limit_error[0]), limit_error[1]
    try:
        resp = requests.get(f"http://simrs.belitung.go.id:3000/api/wsvclaim/pesertaNik?nik={nik}").json()
        #nama  = resp["response"]["data"][0]["peserta"]["nama"]
        #lahir = resp["response"]["data"][0]["peserta"]["tglLahir"]
        #phone = resp["response"]["data"][0]["peserta"]["mr"]["noTelepon"]
        #umur  = resp["response"]["data"][0]["peserta"]["umur"]["umurSekarang"]
        #jenis = resp["response"]["data"][0]["peserta"]["sex"]
        #if jenis in "L":type = "Pria"
        #elif jenis in "P":type = "Perempuan"
        #else:type = None
        return jsonify(
            {
                "creator": "AmmarBN", 
                "result": resp,
                "status": True
            }
        )
    except requests.exceptions.RequestException as e:return jsonify({'error': str(e)})

@ckwalet_bp.route('/ckwalet', methods=['GET'])
def checkwalet():
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
        response_data = []
        ewallets = requests.get('https://api-rekening.lfourr.com/listEwallet').json()['data']
        for ewallet in ewallets:
           wallet_check = requests.get(f'https://api-rekening.lfourr.com/getEwalletAccount?bankCode={ewallet["kodeBank"]}&accountNumber={phone}')
           if wallet_check.json()['status']:
               account_info = wallet_check.json()['data']
               response_data.append({  # Append wallet information to the list
                 'Type Wallet': account_info['bankcode'],
                 'Name': account_info['accountname']
                 })
        return jsonify(
            {
                "creator": "AmmarBN", 
                "result": response_data,
                "status": True
            }
        )
    except requests.exceptions.RequestException as e:return jsonify({'error': str(e)})
if __name__ == '__main__':
    app.run()
