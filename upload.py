from funcs import *
from login import *
import random,string
from requests_toolbelt import MultipartEncoder

class Upload():
    def __init__(self,account: acc) -> None:
        self.isupload=False
        self.acc=account
        self.get_resource()

    def get_resource(self):
        api={"action":"POST_MOBILE_V1_RESOURCE_CSTORE_UPLOADPOLICY","params":{"appId":"10388","clientIp":"","clientId":"","requestId":""}}
        re = requests.post(urls.upload,data=json.dumps(api),headers=self.acc.mheaders,proxies={'http': 'http://192.168.0.104:9000','https':'http://192.168.0.104:9000'}, verify=False)
        try:
            self.res=json.loads(re.text)
            self.uploadUrl=self.res['data']['policyList'][0]['uploadUrl']
            self.expiretime=int(time.time()) + self.res['data']['expireSeconds']
            self.headers={
            "Host": self.uploadUrl[8:],
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Site": "cross-site",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "cors",
            "Origin": "https://m-campus.seewo.com",
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Referer": "https://m-campus.seewo.com/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty"
            }
        except json.decoder.JSONDecodeError:
            print("上传失败： 请求错误")
            print(re.text)
        except KeyError:
            print(self.res['message'])
        return None
    
    def upload(self,file):
        if self.isupload:
            print("该文件已上传: " + self.downloadUrl)
            return None
        data = {
            "key": (None, self.res['data']['policyList'][0]['formFields'][0]['value']),
            "policy": (None, self.res['data']['policyList'][0]['formFields'][1]['value']),
            "q-signature": (None, self.res['data']['policyList'][0]['formFields'][2]['value']),
            "q-key-time": (None, self.res['data']['policyList'][0]['formFields'][3]['value']),
            "q-ak": (None, self.res['data']['policyList'][0]['formFields'][4]['value']),
            "q-sign-algorithm": (None, self.res['data']['policyList'][0]['formFields'][5]['value']),
            "callback": (None, self.res['data']['policyList'][0]['formFields'][6]['value']),
            "success_action_status": (None, self.res['data']['policyList'][0]['formFields'][7]['value']),
            "x:appid": (None, self.res['data']['policyList'][0]['formFields'][8]['value']),
            "x:sessionid": (None, self.res['data']['policyList'][0]['formFields'][9]['value']),
            "x:bucketid": (None, self.res['data']['policyList'][0]['formFields'][10]['value']),
            "file": ('IMG_0188.PNG', open(file, "rb"), "image/png")
        }
        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        multipart = MultipartEncoder(fields=data, boundary=boundary)
        self.headers['Content-Type']=multipart.content_type
        try:
            response = requests.post(self.uploadUrl, headers=self.headers, data=multipart, timeout=(self.expiretime-time.time()),proxies={'http': 'http://192.168.0.104:9000','https':'http://192.168.0.104:9000'}, verify=False)
            uploaded=json.loads(response.text)
            if uploaded["code"] == 0:
                self.isupload=True
                self.downloadUrl=uploaded['data']['downloadUrl']
                uploads: dict
                uploads=json.loads(read_file(uploads_file))
                uploads[file] = (uploaded['data'])
                write_file(uploads_file,uploads)
                print("上传成功: " + self.downloadUrl)
            else:
                print("上传失败: " + response.text)
        except:
            response = None
        return response
