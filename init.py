import time
import os
import json
import base64

qrcode_file = "qrcode.png"
token_file = "tokens.json"
uploads_file = "uploads.json"
if not os.path.isfile(uploads_file):
    with open(uploads_file, "wb") as f:
        f.write(b"{}")
proxies: dict[str, str] = {}# type: ignore
verify=True
headers_nocookie = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "image/avif,image/webp,*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://id.seewo.com/login-iframe?system=mis-admin&callbackIframeUrl=%2F%2Fcampus.seewo.com%2Fcallback-iframe&redirect_url=",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
}


class urls:
    def __init__(self) -> None:
        self.time=str(
        int(time.time()) * 1000
    )
        self.status = "https://campus.seewo.com/soul-bootstrap/seewo-phoenix-blood-server/mobile/user/v1/"
        self.get_last_msg = "https://campus.seewo.com/soul-bootstrap/home-school-service/mobile/kidnote/v1/note/dialogs?userUid="
        self.api = "https://m-campus.seewo.com/class/apis.json?action="
        self.login_api = "https://id.seewo.com/auth/loginApi?_time" + self.time
        self.qrcode_image = "https://id.seewo.com/scan/qrcode?oriSys=mis-admin&t=" + self.time
        self.check_qrcode = "https://id.seewo.com/scan/pcCheckQrcode?type=long&_=" + self.time


