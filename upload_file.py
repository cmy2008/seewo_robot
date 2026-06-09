# -*- coding: utf-8 -*-

import os
from sys import argv

from login import acc
from upload import Upload

def upload_file(account: acc,file,type="image/png"):
    up=Upload(account)
    up.upload(file=file,type=type)
    return up.downloadUrl

if __name__ == "__main__":
    account=acc()
    file=argv[1]
    url=upload_file(account,file)
    print(f"{os.path.basename(file)}：{url}")