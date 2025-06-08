import time


qrcode_file= 'qrcode.png'
token_file = "tokens.json"
proxies: dict[str, str] = {"http": None, "https": None}
headers_nocookie = {
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
class urls():
    status = "https://campus.seewo.com/soul-bootstrap/seewo-phoenix-blood-server/mobile/user/v1/"
    get_last_msg = "https://campus.seewo.com/soul-bootstrap/home-school-service/mobile/kidnote/v1/note/dialogs?userUid="
    get_msg = "https://m-campus.seewo.com/class/apis.json?action=GET_KIDNOTE_V1_BYPARENTUID_BYCHILDUID_NOTES"
    get_stu_info = "https://m-campus.seewo.com/class/apis.json?action=GET_STUDENT_V1_PARENT_BYPARENTID_CHILDREN_LIST"
    send_msg = "https://m-campus.seewo.com/class/apis.json?action=POST_KIDNOTE_V1_NOTE"
    del_msg = "https://m-campus.seewo.com/class/apis.json?action=DELETE_KIDNOTE_V1_NOTE"
    login_api = "https://id.seewo.com/auth/loginApi?_time" + str(int(time.time() * 1000))
    qrcode_image = "https://id.seewo.com/scan/qrcode?oriSys=mis-admin&t=" + str(time.time()*1000)
    check_qrcode = "https://id.seewo.com/scan/pcCheckQrcode?type=long&_=" + str(time.time()*1000)