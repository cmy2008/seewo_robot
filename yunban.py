# -*- coding: utf-8 -*-

from init import *
from login import *
from api import *
import random
from datetime import datetime, date, timedelta

def getpass(account:acc,schoolUid, snCode,time,classUid=""):
    data={
    "schoolUid": schoolUid,
    "snCode": snCode,
    "version": "1",
    "timestamp": time,                 #"1754063970000",
    "classUid": classUid
  }
    return api().action("GET_AUTHORIZATION_V1_USER_OFFLINE_VERIFY",data,account)

def getpass2():
    import pandas.io.clipboard as cb
    account=acc()
    while True:
        url: str
        url=cb.paste()
        if url.startswith("https://id.seewo.com/"):
            snCode=url.split("snCode%3D")[1].split("%26")[0]
            timestamp=url.split("timestamp%3D")[1].split("%26")[0]
            schoolUid=url.split("schoolUid%3D")[1].split("%26")[0]
            print(getpass(account,schoolUid,snCode,timestamp),end="\r")
            # print(snCode+' ' +timestamp)
            time.sleep(0.5)

class yunban:
    def __init__(self,token,schoolid) -> None:
        self.token=token
        self.schoolid=schoolid
        self.headers = {
      'User-Agent': "okhttp/4.8.0",
      'Connection': "Keep-Alive",
      'Accept-Encoding': "gzip",
      'Cookie': f"acw_tc={self.token}"
    }
    def getclasslist(self):
      url = f"https://campus.seewo.com/mis-cloud-route-server/api/classmember/v1/school/{self.schoolid}/classes"
      response = requests.request("GET", url, headers=self.headers)
      return response.json()["data"]
    
    def getnotes(self,uid,parentuid,num):
      url = f"https://campus.seewo.com/mis-cloud-route-server/api/kidnote/v4/parent/{parentuid}/child/{uid}/notes?start={num}&pageSize=1"
      response = requests.request("GET", url, headers=self.headers,verify=False)
      return response.json()["data"]
    
    def getparents(self,uid):
      url = f"https://campus.seewo.com/mis-cloud-route-server/api/kidnote/v1/{uid}/parent/note/count"
      response = requests.request("GET", url, headers=self.headers,verify=False)
      return response.json()["data"]

    def getstulist(self,classid):
      url = f"https://campus.seewo.com/mis-cloud-route-server/api/classmember/v1/school/{self.schoolid}/students?classUids={classid}"
      response = requests.request("GET", url, headers=self.headers, verify=False)
      return response.json()["data"][0]["students"]
    
    def serchstubyname(self,stuname,students):
      for stu in students:
        if stu["name"]==stuname:
          return stu
      return {}

    def serchstubyuid(self,stuname,students):
      for stu in students:
        if stu["uid"]==stuname:
          return stu
      return {}

    def getevents(self,roomUid):
      url = f"https://campus.seewo.com/mis-cloud-route-server/api/attendance/v3/{self.schoolid}/events?roomUid={roomUid}"
      response = requests.request("GET", url, headers=self.headers, verify=False)
      return response.json()["data"]
    
    # Get time from events

    def geteventtime(self,event):
      config = json.loads(event["config"]) # '{"banPaiConfig": {"topEndTime": "07:20", "topStartTime": "06:16"}}'
      return config["banPaiConfig"]["topStartTime"],config["banPaiConfig"]["topEndTime"]
    
    '''
    Random generate attend data
            "attendanceDate": "2025-11-08", this decides the now date
        "attendanceTime": "17:56:05", this should be random between self.geteventtime(event)[0] and event["endTime"]
    '''


    def random_time_in_range(self,start_str: str, end_str: str) -> str:
      """
      生成当天在指定时间范围内的随机时间（包含秒）。
      
      参数:
          start_str: 开始时间，格式 "HH:MM"（例如 "09:00"）
          end_str:   结束时间，格式 "HH:MM"（例如 "17:30"）
      
      返回:
          字符串，格式 "YYYY-MM-DD HH:MM:SS"，为当天在该范围内的随机时间。
      
      注意:
          - 假设 start_str <= end_str（不跨午夜）。
          - 如果结束时间早于或等于开始时间，会抛出 ValueError。
      """
      # 解析时间字符串
      start_time = datetime.strptime(start_str, "%H:%M").time()
      end_time = datetime.strptime(end_str, "%H:%M").time()
      
      # 获取当天日期
      today = date.today()
      
      # 组合成完整的 datetime 对象
      start_dt = datetime.combine(today, start_time)
      end_dt = datetime.combine(today, end_time)
      
      # 检查时间范围有效性
      if end_dt <= start_dt:
          raise ValueError("结束时间必须晚于开始时间（不支持跨天范围）")
      
      # 计算时间间隔的总秒数
      total_seconds = (end_dt - start_dt).total_seconds()
      
      # 生成随机秒数（浮点数，确保秒部分也能随机）
      random_seconds = random.uniform(0, total_seconds)
      
      # 添加随机偏移
      random_dt = start_dt + timedelta(seconds=random_seconds)
      
      # 格式化输出（秒会自动四舍五入到整数）
      return random_dt.strftime("%H:%M:%S")

    def randomtime(self,event):
      # datenow=time.strftime('%Y-%m-%d', time.localtime())
      start=self.geteventtime(event)[0]
      end=event["endTime"]
      return self.random_time_in_range(start,end)

    def attend(self,name,uid,sid,event,date,time,classUid,roomUid):
      payload = {
        "attendanceData": [
          {
            "eventId": event["eventId"],
            "eventVersion": 1,
            "attendanceType": 1,
            "forwardEventType": 10,
            "eventStartTime": self.geteventtime(event)[0],
            "eventAttendTime": event["endTime"],
            "eventEndTime": self.geteventtime(event)[1],
            "classUid": classUid,
            "attendanceDate": date,
            "attendanceTime": time,
            "roomUid": roomUid,
            "userUid": uid,
            "userName": name,
            "userSid": sid
          }
        ]
      }
      print(payload)
      url = f"https://campus.seewo.com/mis-cloud-route-server/api/attendance/v1/{self.schoolid}/data"
      response = requests.post(url, json=payload, headers=self.headers, verify=False)
      return response.json()
    
