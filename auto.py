from main import *
import os, time

filedate=time.strftime('%Y-%m-%d', time.localtime())
def date():
    return '[' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ']: '
def logw(t):
        log=date() + t + '\n'
        dirc='logs/' + filedate + '.log'
        with open(dirc, 'a') as file:
            file.write(log)
        
last_msg = ' '
msg_id=0
get_id=0
while True:
    time.sleep(1)
    try:
        get_id=get_msg_id(1)
    except Exception as err:
        log="[ERROR] 获取消息ID失败: " + str(err)
        logw(log)
    if msg_id != get_id:
        try:
            last_msg=get_msg_context(1)
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
            send = os.popen(command).read()
            print(send)
            send_msg(send[:199],1)
        except:
            log="[ERROR] 发送失败"
            logw(log)
