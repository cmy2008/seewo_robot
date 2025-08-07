import base64
import json
import time
import os

filedate=time.strftime('%Y-%m-%d', time.localtime())

def encode_json(data: dict):
    return base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")

def pxdecode(data: dict):
    return base64.b64decode(data["data"][7:])

def pxencode(data: dict):
    return {"pxSafeData": f"scData:{encode_json(data)}"}

def read_file(file: str):
    with open(file, "r") as f:
        content = f.read()
        return content

def write_file(file: str,data: bytes):
    with open(file, "wb") as f:
        f.write(data)
        f.close
    return True

def load_json(file: str):
    return json.loads(read_file(file))


def date():
    return '[' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ']: '

def logw(t: str):
        log=date() + t + '\n'
        log_dir='logs/'
        dirc=log_dir + filedate + '.log'
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)
        with open(dirc, 'a') as file:
            file.write(log)