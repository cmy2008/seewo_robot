from qrcode import *
from init import *
import json, requests
import time


def get_cookies():
    re = requests.get(url=urls["login_api"], headers=headers3, proxies=proxies)
    return requests.utils.dict_from_cookiejar(re.cookies)


def download_qrcode():
    re = requests.get(urls["qrcode_image"], cookies=get_cookies(), proxies=proxies)
    content = re.content
    with open(qrcode_file, "wb") as f:
        f.write(content)
    return requests.utils.dict_from_cookiejar(re.cookies)


def check_qrcode(cookies):
    re = requests.get(
        urls["check_qrcode"] + str(int(time.time() * 1000)),
        headers=headers3,
        cookies=cookies,
        proxies=proxies,
    )
    return json.loads(re.text)


def login():
    cookies = download_qrcode()
    print_qrcode(qrcode_file)
    status = 200
    while status == 200 or 201:
        data = check_qrcode(cookies)["data"]
        status = data["statusCode"]
        message = data["message"]
        print(str(int(time.time())) + ": " + message, end="\r")
    else:
        if status == 300 or 500:
            print(message)
            return False
        else:
            print(message + str(status))
            print(data)
            with open("tokens.json", "w") as f:
                f.write(json.dumps(data))
                f.close
            return True
