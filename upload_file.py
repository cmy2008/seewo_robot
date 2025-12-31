from login import *
from upload import *
from sys import argv

def upload_file(account: acc,file,type="image/png"):
    up=Upload(account)
    up.upload(file=file,type=type)
    return up.downloadUrl

if __name__ == "__main__":
    account=acc()
    file=argv[1]
    url=upload_file(account,file)
    print(f"{os.path.basename(file)}：{url}")