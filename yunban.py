from init import *
from login import *
from api import *

def getpass(account:acc,schoolUid, snCode,time,classUid=""):
    data={
    "schoolUid": schoolUid,
    "snCode": snCode,
    "version": "1",
    "timestamp": time,                 #"1754063970000",
    "classUid": classUid
  }
    return api().action("GET_AUTHORIZATION_V1_USER_OFFLINE_VERIFY",data,account)