import requests
import json
from funcs import *
from login import *
from stu import *

class msg():
    def __init__(self,account: acc, student: stu) -> None:
        self.acc=account
        self.stu=student
    def get_last(self):
        #TODO: 异常处理
        re = requests.get(urls.get_last_msg + self.acc.uid, headers=self.acc.headers, proxies=proxies)
        msg_o = json.loads(re.text)["data"]
        if msg_o is None:
            return "[ERROR] 无法获取消息体"
        if msg_o == []:
            return "[INFO] 无消息"
        elif msg_o[0]["lastMsgTips"] == '':
            return "[INFO] 消息为空"
        return msg_o[0]["lastMsgTips"]


    def get(self,count: int):
        data = {
            "action": "GET_KIDNOTE_V1_BYPARENTUID_BYCHILDUID_NOTES",
            "params": {
                "page": 1,
                "pageSize": count,
                "start": 1,
                "parentUid": self.acc.uid,
                "childUid": self.stu.userUid,
            },
        }
        re = requests.post(
            urls.get_msg, headers=self.acc.headers2, data=json.dumps(data), proxies=proxies
        )
        return json.loads(decode(json.loads(re.text)["data"]))


    def get_content(self,count:int):
        return self.get(count)["result"][0]["content"]

    def send(self,content:str,type:int,resUrl='',voiceLength=0,resConfig=''):
        data = {
            "action": "POST_KIDNOTE_V1_NOTE",
            "params": {
                "schoolUid": self.stu.schoolUid,
                "classUid": self.stu.classUid,
                "senderUid": self.acc.uid,
                "receiverUid": self.stu.userUid,
                "senderType": "parent",
                "type": type,
            },
        }
        match type:
            case 0:
                data['params']["content"]=content
            case 1:
                data['params']["content"]=content
            case 3:
                data['params']['voiceLength'] = voiceLength
                data['params']['resUrl'] = resUrl
            case 6:
                data['params']['resUrl'] = resUrl
                data['params']['resConfig'] = resConfig
        re = requests.post(
            urls.send_msg, headers=self.acc.headers2, data=json.dumps(data), proxies=proxies
        )
        code = json.loads(re.text)["statusCode"]
        if code == -500:
            print("发送失败")
            return False
        elif code == 200:
            print("发送成功：" + content)
            return True
        else:
            print("unknown error:")
            print(re.text)


    def get_id(self,count:int):
        id=self.get(count)["result"][0]["id"]
        return id


    def delete(self,count:int):
        id = self.get_id(count)
        data = {"action": "DELETE_KIDNOTE_V1_NOTE", "params": {"ids": [id]}}
        re = requests.post(
            urls.del_msg, headers=self.acc.headers2, data=json.dumps(data), proxies=proxies
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