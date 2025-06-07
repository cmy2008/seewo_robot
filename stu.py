from init import *
import requests
from login import *

class stu():
    def __init__(self,acc: acc,count=0) -> None:
        self.acc=acc
        info=self.info()[count]
        self.schoolUid = info["schoolUid"]
        self.classUid = info["classUid"]
        self.userUid = info["userUid"]
    
    def info(self)->dict:
        data = {
            "action": "GET_STUDENT_V1_PARENT_BYPARENTID_CHILDREN_LIST",
            "params": {
                "pxSafeData": "scData:"
                + base64.b64encode(json.dumps({"parentId": self.acc.uid}).encode("utf-8")).decode(
                    "utf-8"
                )
            },
        }
        re = requests.post(
            urls.get_stu_info, headers=self.acc.mheaders, data=json.dumps(data), proxies=proxies
        )
        data=json.loads(decode(json.loads(re.text)["data"]))
        if data == []:
            print("错误：未添加学生")
            exit()
        return data