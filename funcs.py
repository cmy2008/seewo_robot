import base64
import json
import time

filedate=time.strftime('%Y-%m-%d', time.localtime())
def decode(data):
    return base64.b64decode(data[7:])

def read_file(file):
    with open(file, "r") as f:
        context = f.read()
        return context


def load_json(file):
    return json.loads(read_file(file))


def date():
    return '[' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ']: '

def logw(t):
        log=date() + t + '\n'
        dirc='logs/' + filedate + '.log'
        with open(dirc, 'a') as file:
            file.write(log)