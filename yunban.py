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
      response = requests.request("GET", url, headers=self.headers, verify=False)
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
      start_h,start_m=map(int,start.split(":"))
      end_h,end_m=map(int,end.split(":"))
      if start_h==end_h:
        rand_m=random.randint(start_m,end_m-1)
        return f"{start_h:02d}:{rand_m:02d}:{random.randint(0,59):02d}"
      else:
        rand_h=random.randint(start_h,end_h)
        if rand_h==start_h:
          rand_m=random.randint(start_m,59)
        elif rand_h==end_h:
          rand_m=random.randint(0,end_m)
        else:
          rand_m=random.randint(0,59)
        return f"{rand_h:02d}:{rand_m:02d}:{random.randint(0,59):02d}"
    
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
    
