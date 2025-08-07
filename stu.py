from init import *
import requests
from login import *
from api import *

class stu():
    def __init__(self,acc: acc,count=0) -> None:
        self.acc=acc
        info=self.info()[count]
        self.schoolUid = info["schoolUid"]
        self.classUid = info["classUid"]
        self.userUid = info["userUid"]

    def info(self)->dict:
        data = {"parentId": self.acc.uid}
        result=json.loads(pxdecode(api().action("GET_STUDENT_V1_PARENT_BYPARENTID_CHILDREN_LIST",pxencode(data),self.acc)))
        if result == []:
            print("错误：未添加学生")
            # exit()
        return result

    def get_stu(self,name):
        data={"schoolUid":self.schoolUid,"classUid":self.classUid,"name":name}
        return json.loads(pxdecode(api().action("POST_STUDENT_V1_BYSCHOOLUID_CLASS_BYCLASSUID_STUDENTS",pxencode(data),self.acc)))
    
    def add_stu(self, stu_uid):
        pass