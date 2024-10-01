import time

qrcode_file= 'qrcode.png'
token_file = "tokens.json"
headers = {
    "x-info-sign": "",
    "user-agent": "Dart/2.18 (dart:io)",
    "accept": "application/json,*/*",
    "x-auth-app": "seewo-yunban-mobile",
    "x-auth-appcode": "seewo-yunban-mobile",
    "cookie": "",
    "x-auth-token": "",
    "accept-encoding": "gzip",
    "host": "campus.seewo.com",
    "x-app-version": "50",
    "x-app-platform": "Android",
}
headers2 = {
    "x-stale-if-timeout": "enable",
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Linux; Android 9; Nexus 5 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36",
    "content-type": "application/json",
    "origin": "https://m-campus.seewo.com",
    "x-requested-with": "com.seewo.cc.pro",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-PH,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": "",
}
headers3 = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
  "Accept": "image/avif,image/webp,*/*",
  "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
  "Accept-Encoding": "gzip, deflate, br",
  "Connection": "keep-alive",
  "Referer": "https://id.seewo.com/login-iframe?system=mis-admin&callbackIframeUrl=%2F%2Fcampus.seewo.com%2Fcallback-iframe&redirect_url=",
  "Sec-Fetch-Dest": "image",
  "Sec-Fetch-Mode": "no-cors",
  "Sec-Fetch-Site": "same-origin"
}
proxies = {"http": "http://192.168.1.12:9000", "https": None}
urls = {
    "status": "https://campus.seewo.com/soul-bootstrap/seewo-phoenix-blood-server/mobile/user/v1/",
    "get_last_msg": "https://campus.seewo.com/soul-bootstrap/home-school-service/mobile/kidnote/v1/note/dialogs?userUid=",
    "get_msg": "https://m-campus.seewo.com/class/apis.json?action=GET_KIDNOTE_V1_BYPARENTUID_BYCHILDUID_NOTES",
    "get_stu_info": "https://m-campus.seewo.com/class/apis.json?action=GET_STUDENT_V1_PARENT_BYPARENTID_CHILDREN_LIST",
    "send_msg": "https://m-campus.seewo.com/class/apis.json?action=POST_KIDNOTE_V1_NOTE",
    "del_msg": "https://m-campus.seewo.com/class/apis.json?action=DELETE_KIDNOTE_V1_NOTE",
    "login_api": "https://id.seewo.com/auth/loginApi?_time"
    + str(int(time.time() * 1000)),
    "qrcode_image":"https://id.seewo.com/scan/qrcode?oriSys=mis-admin&t="+ str(time.time()*1000),
    "check_qrcode":"https://id.seewo.com/scan/pcCheckQrcode?type=long&_="
}