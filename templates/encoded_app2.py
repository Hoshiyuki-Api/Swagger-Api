import requests
import json
import os,sys

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# URL for various services
urls = {
    "dana": "https://checker.orderkuota.com/api/checkname/produk/a8ff7bf219/24/1897292/dana",
    "shopeepay": "https://checker.orderkuota.com/api/checkname/produk/a8ff7bf219/24/1897292/shopeepay",
    "gopay": "https://checker.orderkuota.com/api/checkname/produk/a8ff7bf219/24/1897292/gopay",
    "ovo": "https://checker.orderkuota.com/api/checkname/produk/a8ff7bf219/24/1897292/ovo",
    "gopay_driver": "https://checker.orderkuota.com/api/checkname/produk/a8ff7bf219/24/1897292/gopay_driver",
    "ruparupa": "https://wapi.ruparupa.com/klk/check-membership?user=%2B62",
    "tokopedia": "https://gql.tokopedia.com/graphql/checkAccount",
    "mister_aladin": "https://m.misteraladin.com/api/members/v2/auth/login-phone-number-check"
}

# Mapping application names
app_names = {
    "dana": "DANA",
    "shopeepay": "ShopeePay",
    "gopay": "GoPay",
    "ovo": "OVO",
    "gopay_driver": "GoPay Driver",
    "ruparupa": "Rupa Rupa",
    "tokopedia": "Tokopedia",
    "mister_aladin": "Mister Aladin"
}

# Function to check Tokopedia
def check_tokopedia(phone_number):
    headers_tokopedia = {
        "Host": "gql.tokopedia.com",
        "content-length": "203",
        "sec-ch-ua-platform": "Linux",
        "x-version": "e7959d2",
        "sec-ch-ua": "Google Chrome;v=131, Chromium;v=131, Not_A Brand;v=24",
        "sec-ch-ua-mobile": "?0",
        "x-source": "tokopedia-lite",
        "x-tkpd-akamai": "rgsc",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "accept": "*/*",
        "content-type": "application/json",
        "x-tkpd-lite-service": "oauth",
        "origin": "https://www.tokopedia.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.tokopedia.com/login",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6",
    }

    data_tokopedia = [  
        {  
            "operationName": "checkAccount",  
            "variables": {"id": phone_number.lstrip("+")},  # Remove '+' if present  
            "query": """mutation checkAccount($id: String!) {  
                registerCheck(id: $id) {  
                    isExist  
                    errors  
                    uh  
                    __typename  
                }  
            }"""  
        }  
    ]  

    response = requests.post(urls['tokopedia'], headers=headers_tokopedia, json=data_tokopedia)  

    if response.status_code == 200:  
        data = response.text  
        if '"isExist":true' in data:  
            return "YES"  
        else:  
            return "NO"  
    else:  
        return f"Error Tokopedia: {response.status_code}"

# Function to check Mister Aladin
def check_mister_aladin(phone_number):
    headers_mister_aladin = {
        "Host": "m.misteraladin.com",
        "content-length": "63",
        "x-platform": "mobile-web",
        "authorization": "",
        "sec-ch-ua-platform": "Android",
        "accept-language": "id",
        "sec-ch-ua": "Google Chrome;v=131, Chromium;v=131, Not_A Brand;v=24",
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://m.misteraladin.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://m.misteraladin.com/account",
        "accept-encoding": "gzip, deflate, br, zstd",
    }

    data_mister_aladin = {  
        "phone_number_country_code": "62",  
        "phone_number": phone_number.lstrip("0")  # Remove '0' if present  
    }  

    response = requests.post(urls['mister_aladin'], headers=headers_mister_aladin, json=data_mister_aladin)  

    if response.status_code == 422:  
        data = response.text  
        if "Nomor telepon yang kamu masukkan belum terdaftar." in data:  
            return "NO"  
        else:  
            return "YES"  
    else:  
        return f"Error Mister Aladin: {response.status_code}"

# Function to check Rupa Rupa
def check_ruparupa(phone_number):
    headers_ruparupa = {
        "Host": "wapi.ruparupa.com",
        "x-frontend-type": "mobile",
        "sec-ch-ua-platform": "Android",
        "sec-ch-ua": "Google Chrome;v=131, Chromium;v=131, Not_A Brand;v=24",
        "sec-ch-ua-mobile": "?1",
        "user-platform": "mobile",
        "rr-sid": "H7YBz1735571031gPVrUhjUNK",
        "accept": "application/json",
        "b2b-type": "non-b2b",
        "x-company-name": "ruparupa",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "origin": "https://www.ruparupa.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.ruparupa.com/auth/login?itm_source=tahu-sticky-Masuk&itm_campaign=homepage&itm_device=mobile",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7,ms;q=0.6",
        "priority": "u=1, i"
    }

#    data_ruparupa = {
#        "user": phone_number.lstrip("0")  # Remove '0' if present
#    }

    response = requests.get(urls['ruparupa']+phone_number, headers=headers_ruparupa) 

    if response.status_code == 200:  
        dat = response.json()  
        if dat["data"]["next_action"] == "login":  
            return "YES"  
        else:  
            return "NO"  
    else:  
        return f"Error Rupa Rupa: {response.status_code}"

# Main function to check phone registration status
def check_phone_registration(phone_number):
    results = []  

    # Check phone number in various services  
    tokopedia_result = check_tokopedia(phone_number)  
    results.append({"service": "Tokopedia", "phone": phone_number, "registered": tokopedia_result})  

    mister_aladin_result = check_mister_aladin(phone_number)  
    results.append({"service": "Mister Aladin", "phone": phone_number, "registered": mister_aladin_result})  

    ruparupa_result = check_ruparupa(phone_number)  
    results.append({"service": "Rupa Rupa", "phone": phone_number, "registered": ruparupa_result})  

    # Check other services  
    for id_name, url in urls.items():  
        if id_name not in ["tokopedia", "mister_aladin", "ruparupa"]:  
            headers = {  
                "Content-Type": "application/x-www-form-urlencoded",  
                "Host": "checker.orderkuota.com",  
                "Connection": "Keep-Alive",  
                "Accept-Encoding": "gzip",  
                "User-Agent": "okhttp/4.12.0",  
            }  
            data = {  
                "phoneNumber": phone_number,  
                "app_reg_id": "fhdH0F-8Rrmt02q3H31coo:APA91bGs6KaglRvhPVMA9LK3aMs4iDBHnXaGX-MucQZ7-o1s1KMkOgdZA9Qm9zcX19qInYGBu0gmnPVFWG7eRJ-h05qe6e9u-ruCtSQYMhPyHpY5ExLauBp_ejOS-pJQB9EiyL9HeamO",  
                "phone_android_version": "14",  
                "app_version_code": "241212",  
                "phone_uuid": "fhdH0F-8Rrmt02q3H31coo",  
                "auth_username": "ammarbn",  
                "customerId": "",  
                "auth_token": "1897292:TsEZ8fI2JGykpA3SO5dv6j4Wul1CbUPY",  
                "app_version_name": "24.12.12",  
                "phone_model": "23021RAA2Y",  
            }  

            response = requests.post(url, headers=headers, data=data)  
            response_text = response.text  
            response_dict = json.loads(response.text)  
            response_true = response_dict["message"]  

            if "TIDAK TERDAFTAR" in response_text:  
                registered = "NO"  
            else:  
                registered = f"{response_true} (YES)"  

            app_name = app_names.get(id_name, "Unknown App")  
            results.append({"service": app_name, "phone": phone_number, "registered": registered})  

    return results

# Input phone number
try:
    clear_screen()
    print ("""
         ______   _       __      ____     __
        / ____/  | |     / /___ _/ / /__  / /_
       / __/_____| | /| / / __ `/ / / _ \/ __/
      / /__/_____/ |/ |/ / /_/ / / /  __/ /_
     /_____/     |__/|__/\__,_/_/_/\___/\__/
  [ Tools Created By MataHacker (matahacker.id ]""")
    phone_number = input("\n[?] Input Phone (08xxx): ")

    # Check phone registration status
    results = check_phone_registration(phone_number)

    # Print results
    for result in results:
        print(f"[•] {result['service']}\n   - Phone: {result['phone']}\n   - Registered: {result['registered']}")
except KeyboardInterrupt:
    sys.exit()
except requests.exceptions.ConnectionError:
    sys.exit("[!] Koneksi Anda Tidak Stabil")
except KeyError:
    sys.exit("[!] Kesalahan Tidak Terduga, Coba Lagi Nanti")
