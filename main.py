# -*- coding: utf-8 -*-

import json, base64, requests, time
from datetime import datetime

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


def read_file(file):
    with open(file, "r") as f:
        context = f.read()
        return context


def load_json(file):
    return json.loads(read_file(file))


def decode(data):
    return base64.b64decode(data[7:])


def get_info(file):
    return json.loads(decode(load_json(file)["data"]))

def status(re):
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
        print(re)
        return False

def check_status():
    re = requests.get(urls["status"], headers=headers)
    return status(re.text)


def get_stu_info():
    data = {
        "action": "GET_STUDENT_V1_PARENT_BYPARENTID_CHILDREN_LIST",
        "params": {
            "pxSafeData": "scData:"
            + base64.b64encode(json.dumps({"parentId": uid}).encode("utf-8")).decode(
                "utf-8"
            )
        },
    }
    re = requests.post(urls["get_stu_info"], headers=headers2, data=json.dumps(data))
    return json.loads(decode(json.loads(re.text)["data"]))


def get_last_msg():
    re = requests.get(urls["get_last_msg"], headers=headers)
    return json.loads(re.text)["data"][0]["lastMsgTips"]


def get_msg(count):
    data = {
        "action": "GET_KIDNOTE_V1_BYPARENTUID_BYCHILDUID_NOTES",
        "params": {
            "page": 1,
            "pageSize": count,
            "start": 1,
            "parentUid": uid,
            "childUid": userUid,
        },
    }
    re = requests.post(urls["get_msg"], headers=headers2, data=json.dumps(data))
    return json.loads(decode(json.loads(re.text)["data"]))


def get_msg_context(count):
    return get_msg(count)["result"][0]["content"]


def send_msg(context):
    data = {
        "action": "POST_KIDNOTE_V1_NOTE",
        "params": {
            "schoolUid": schoolUid,
            "classUid": classUid,
            "senderUid": uid,
            "receiverUid": userUid,
            "senderType": "parent",
            "type": 1,
            "content": context,
        },
    }
    re = requests.post(urls["send_msg"], headers=headers2, data=json.dumps(data))
    code = json.loads(re.text)["statusCode"]
    if code == -500:
        print("发送失败")
        return False
    elif code == 200:
        print("发送成功：" + context)
        return True
    else:
        print("unknown error:")
        print(re.text)


def get_msg_id(count):
    return get_msg(count)["result"][0]["id"]


def del_msg(count):
    id = get_msg_id(count)
    data = {"action": "DELETE_KIDNOTE_V1_NOTE", "params": {"ids": [id]}}
    re = requests.post(urls["del_msg"], headers=headers2, data=json.dumps(data))
    code = json.loads(re.text)["statusCode"]
    if code == -500:
        print("删除失败")
        return False
    elif code == 200:
        print("删除成功：")
        return True
    else:
        print("unknown error:")
        print(re.text)


info = get_info(token_file)
uid = info["uid"]
urls = {
    "status": "https://campus.seewo.com/soul-bootstrap/seewo-phoenix-blood-server/mobile/user/v1/"
    + uid
    + "/functionality",
    "get_last_msg": "https://campus.seewo.com/soul-bootstrap/home-school-service/mobile/kidnote/v1/note/dialogs?userUid="
    + uid,
    "get_msg": "https://m-campus.seewo.com/class/apis.json?action=GET_KIDNOTE_V1_BYPARENTUID_BYCHILDUID_NOTES",
    "get_stu_info": "https://m-campus.seewo.com/class/apis.json?action=GET_STUDENT_V1_PARENT_BYPARENTID_CHILDREN_LIST",
    "send_msg": "https://m-campus.seewo.com/class/apis.json?action=POST_KIDNOTE_V1_NOTE",
    "del_msg": "https://m-campus.seewo.com/class/apis.json?action=DELETE_KIDNOTE_V1_NOTE",
}
headers["cookie"] = info["token"]
headers["x-auth-token"] = info["token"]
headers2["cookie"] = "x-auth-token=" + info["token"]
if check_status() ==False:
    exit()
stu_info = get_stu_info()[0]
schoolUid = stu_info["schoolUid"]
classUid = stu_info["classUid"]
userUid = stu_info["userUid"]
