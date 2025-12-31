from init import *
from login import *
from api import *
import random

def getpass(account:acc,schoolUid, snCode,time,classUid=""):
    data={
    "schoolUid": schoolUid,
    "snCode": snCode,
    "version": "1",
    "timestamp": time,                 #"1754063970000",
    "classUid": classUid
  }
    return api().action("GET_AUTHORIZATION_V1_USER_OFFLINE_VERIFY",data,account)
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
    def randomtime(self,event):
      start=self.geteventtime(event)[0]
      end=event["endTime"]
      s_t=time.strptime(start+" "+start, "%Y-%m-%d %H:%M")
      e_t=time.strptime(end, "%H:%M")
      plus=random.randint(0,t)

    
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
    
