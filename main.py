# -*- coding: utf-8 -*-

import os, json, base64, requests
from init import *
from login import *


def read_file(file):
    with open(file, "r") as f:
        context = f.read()
        return context


def load_json(file):
    return json.loads(read_file(file))


def decode(data):
    return base64.b64decode(data[7:])


def get_info(file):
    return load_json(file)


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
    re = requests.get(
        urls["status"] + uid + "/functionality", headers=headers, proxies=proxies
    )
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
    re = requests.post(
        urls["get_stu_info"], headers=headers2, data=json.dumps(data), proxies=proxies
    )
    data=json.loads(decode(json.loads(re.text)["data"]))
    if data == []:
        print("错误：未添加学生")
        exit()
    return data


def get_last_msg():
    re = requests.get(urls["get_last_msg"] + uid, headers=headers, proxies=proxies)
    msg_o = json.loads(re.text)["data"]
    if msg_o == []:
        return "[INFO] 无消息"
    elif msg_o == '':
        return "[INFO] 消息为空"
    return msg_o[0]["lastMsgTips"]


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
    re = requests.post(
        urls["get_msg"], headers=headers2, data=json.dumps(data), proxies=proxies
    )
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
    re = requests.post(
        urls["send_msg"], headers=headers2, data=json.dumps(data), proxies=proxies
    )
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
    re = requests.post(
        urls["del_msg"], headers=headers2, data=json.dumps(data), proxies=proxies
    )
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


if not os.path.exists(token_file):
    a = login()
    if not a:
        exit()
info = get_info(token_file)
uid = info["userId"]
headers["cookie"] = info["token"]
headers["x-auth-token"] = info["token"]
headers2["cookie"] = "x-auth-token=" + info["token"]
if check_status() == False:
    a = login()
    if not a:
        exit()
stu_info = get_stu_info()[0]
schoolUid = stu_info["schoolUid"]
classUid = stu_info["classUid"]
userUid = stu_info["userUid"]
