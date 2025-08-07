from init import *
import requests
from login import *

class api:
    def __init__(self) -> None:
        pass

    def action(self, type: str, params: dict, account: acc) -> dict:
        encode_data = {"action": type, "params": params}
        re=requests.post(
            "https://m-campus.seewo.com/class/apis.json?action=" + type, headers=account.mheaders, data=json.dumps(encode_data), verify=verify
        )
        return json.loads(re.text)

    