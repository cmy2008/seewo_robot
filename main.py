# -*- coding: utf-8 -*-

# TODO: 多学生选择
import os
os.chdir(os.path.dirname(__file__))
print("当前路径："+os.getcwd())
from init import *
from login import *
from funcs import *
from stu import *
from msg import *
from upload import *
from yunban import *

account=acc()
student=stu(account)
stu_msg=msg(account,student)

def upload_file(account: acc,file,type="image/png"):
    up=Upload(account)
    up.upload(file=file,type=type)
    return up.downloadUrl

def send_msg(msg: msg,send: str):
    try:
        # TODO: 超时处理
        print(send)
        stu_msg.send(send[:199],1)
    except:
        log="[ERROR] 发送失败"
        logw(log)

def send_audio(file):
    stu_msg.send(os.path.basename(file),1)
    url=upload_file(account,file)
    stu_msg.send('',3,url,666)

def main():
    last_msg = ' '
    msg_id=0
    get_id=0
    while True:
        time.sleep(1)
        try:
            get_id=stu_msg.get_id(1)
        except Exception as err:
            log="[ERROR] 获取消息ID失败: " + str(err)
            logw(log)
        if msg_id != get_id:
            try:
                last_msg=stu_msg.get_content(1)
                msg_id=get_id
            except Exception as err:
                log="[ERROR] 消息获取失败"
                logw(log)
            logw(last_msg)
            print(datenow()+last_msg)
        else:
            last_msg=" "
        if last_msg == '':
            last_msg = ' '
        if last_msg[0] == "/":
            command = last_msg[1:]
            args=command.split(' ')
            match args[0]:
                case "getpass":
                    send_msg(stu_msg,str(getpass(account,student.schoolUid,args[1],args[2])))
                case "发送音乐":
                    if os.path.exists("music")==False:
                        os.mkdir("music")
                    filelist=os.listdir("music")
                    for file in filelist:
                        send_audio("music/"+file)
                case _:
                    send_msg(stu_msg,os.popen(command).read())

if __name__ == "__main__":
    main()