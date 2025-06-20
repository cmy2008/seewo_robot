# -*- coding: utf-8 -*-

# TODO: 多学生选择
import os
from init import *
from login import *
from funcs import *
from stu import *
from msg import *
from upload import *

account=acc()
student=stu(account)
stu_msg=msg(account,student)

def upload_file(account: acc,file,type="image/png"):
    up=Upload(account)
    up.upload(file=file,type=type)
    return up.downloadUrl

def send_audio(file):
    stu_msg.send(file,1)
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
            print(date()+last_msg)
        else:
            last_msg=" "
        if last_msg == '':
            last_msg = ' '
        if last_msg[0] == "/":
            command = last_msg[1:]
            try:
                # TODO: 超时处理
                send = os.popen(command).read()
                print(send)
                stu_msg.send(send[:199],1)
            except:
                log="[ERROR] 发送失败"
                logw(log)

if __name__ == "__main__":
    main()