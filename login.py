from qrcode import *
from init import *
from funcs import *
import json, requests
import time
import os

class acc():
    def __init__(self,type=0) -> None:
        if type==0:
            if not os.path.exists(token_file):
                self.__init__(type=1)
                return None
            else:
                info = load_json(token_file)
        elif type==1:
            login()
            info = load_json(token_file)
        else:
            return None
        self.uid = info["userId"]
        self.headers = {
            "x-info-sign": "",
            "user-agent": "Dart/2.18 (dart:io)",
            "accept": "application/json,*/*",
            "x-auth-app": "seewo-yunban-mobile",
            "x-auth-appcode": "seewo-yunban-mobile",
            "cookie": f"x-auth-appCode=seewo-yunban-mobile; x-auth-token={info['token']}; x-token={info['token']}",
            "accept-encoding": "gzip",
            "content-type": "application/json",
            "host": "campus.seewo.com"
        }
        self.mheaders = {
            "x-info-sign": "",
            "user-agent": "Mozilla/5.0 (Linux; Android 9; Nexus 5 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36",
            "accept": "application/json,*/*",
            "x-auth-app": "seewo-yunban-mobile",
            "x-auth-appcode": "seewo-yunban-mobile",
            "cookie": f"x-auth-appCode=seewo-yunban-mobile; x-auth-token={info['token']}; x-token={info['token']}",
            "accept-encoding": "gzip",
            "content-type": "application/json"
        }
        if not self.check_status():
            self.__init__(type=1)
            return None
        return None
    
    def status(self,re):
        code = json.loads(re)["statusCode"]
        if code == -500:
            print("登录失败：token无效")
            return False
        elif code == -505:
            print("登录失败：token已过期")
            return False
        elif code == 200:
            return True
        else:
            print(re,end='\n')
            return False
        
    def check_status(self):
        re = requests.get(
            urls().status + self.uid + "/functionality", headers=self.headers, proxies=proxies, verify=verify
        )
        return self.status(re.text)

def get_cookies():
    re = requests.get(url=urls().login_api, headers=headers_nocookie, proxies=proxies)
    return requests.utils.dict_from_cookiejar(re.cookies)


def download_qrcode():
    re = requests.get(urls().qrcode_image, cookies=get_cookies(), proxies=proxies)
    content = re.content
    write_file(qrcode_file, content)
    return requests.utils.dict_from_cookiejar(re.cookies)


def check_qrcode(cookies):
    re = requests.get(
        urls().check_qrcode,
        headers=headers_nocookie,
        cookies=cookies,
        proxies=proxies,
    )
    return json.loads(re.text)


def login():
    cookies = download_qrcode()
    print_qrcode(qrcode_file)
    status = 200
    while status == 200 or status == 201:
        data = check_qrcode(cookies)["data"]
        status = data["statusCode"]
        message = data["message"]
        print(str(int(time.time())) + ": " + message + str(status), end="\r")
    else:
        if status == 202:
            write_file("tokens.json", json.dumps(data).encode())
            return True
        else:
            return False
