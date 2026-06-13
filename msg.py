import requests
import json
from funcs import *
from login import *
from stu import *


class msg:
    def __init__(self, account: acc, student: stu) -> None:
        self.acc = account
        self.stu = student

    def get_last(self):
        # TODO: 异常处理
        re = requests.get(
            urls().get_last_msg + self.acc.uid,
            headers=self.acc.headers,
            proxies=proxies,
        )
        msg_o = json.loads(re.text)["data"]
        if msg_o is None:
            return "[ERROR] 无法获取消息体"
        if msg_o == []:
            return "[INFO] 无消息"
        elif msg_o[0]["lastMsgTips"] == "":
            return "[INFO] 消息为空"
        return msg_o[0]["lastMsgTips"]

    def get(self, count: int):
        data = {
            "page": 1,
            "pageSize": count,
            "start": 1,
            "parentUid": self.acc.uid,
            "childUid": self.stu.userUid,
        }
        return json.loads(
            pxdecode(
                api().action(
                    "GET_KIDNOTE_V1_BYPARENTUID_BYCHILDUID_NOTES", data, self.acc
                )
            )
        )

    def get_content(self, count: int):
        return self.get(count)["result"][0]["content"]

    def send(self, content: str, type: int, resUrl="", voiceLength=0, resConfig=""):
        data = {
            "schoolUid": self.stu.schoolUid,
            "classUid": self.stu.classUid,
            "senderUid": self.acc.uid,
            "receiverUid": self.stu.userUid,
            "senderType": "parent",
            "type": type,
        }
        match type:
            case 0:
                data["content"] = content
            case 1:
                data["content"] = content
            case 2:
                data["resUrl"] = resUrl
            case 3:
                data["voiceLength"] = voiceLength
                data["resUrl"] = resUrl
            case 4:
                data["resUrl"] = resUrl
            case 5:
                data["resUrl"] = resUrl
            case 6:
                data["resUrl"] = resUrl
                data["resConfig"] = resConfig
        post = api().action("POST_KIDNOTE_V1_NOTE", data, self.acc)
        code = post["statusCode"]
        if code == -500:
            print("发送失败")
            return False
        elif code == 200:
            print("发送成功：" + content)
            return True
        else:
            print(f"unknown error: {post}")
            return False

    def get_id(self, count: int) -> int:
        result = self.get(count)["result"]
        if not result:
            return 0
        return result[0]["id"]

    def get_all_ids(self, count: int) -> list[int]:
        """获取多条消息的ID列表，按时间正序排列（旧→新）"""
        result = self.get(count).get("result", [])
        return [m["id"] for m in reversed(result)]

    def get_content_by_index(self, count: int, index: int) -> str:
        """获取第index条消息的内容（0=最新）"""
        return self.get(count)["result"][index]["content"]

    def get_msg_detail(self, count: int, index: int) -> dict:
        """获取第index条消息的完整信息（0=最新）"""
        return self.get(count)["result"][index]

    def get_earlier_messages(self, before_id: int, count: int = 50) -> list[dict]:
        """获取指定ID之前的更早消息（用于滚动加载历史）

        Args:
            before_id: 获取此ID之前的消息
            count: 获取数量

        Returns:
            消息列表，按时间正序排列（旧→新）
        """
        # 获取足够多的消息，然后筛选
        result = self.get(count * 2).get("result", [])
        # 筛选 ID < before_id 的消息
        earlier = [m for m in result if m.get("id", 0) < before_id]
        # 按时间正序排列（旧→新）
        return list(reversed(earlier[:count]))

    def get_all_messages_until_earliest(
        self, start_id: int, batch_size: int = 50, delay: float = 2.0
    ) -> list[dict]:
        """获取从start_id开始的所有历史消息直到最早（用于全量同步）

        Args:
            start_id: 开始获取的消息ID
            batch_size: 每次获取数量
            delay: 每次请求间隔（防风控）

        Returns:
            所有消息列表，按时间正序排列（旧→新）
        """
        all_messages = []
        current_id = start_id

        while True:
            # 获取更早的消息
            earlier = self.get_earlier_messages(current_id, batch_size)
            if not earlier:
                break  # 已经是最早的消息

            all_messages.extend(earlier)
            # 更新current_id为获取到的最早消息ID
            current_id = earlier[0].get("id", current_id)

            # 如果获取的数量少于batch_size，说明已经到最早
            if len(earlier) < batch_size:
                break

            # 等待一段时间（防风控）
            import time

            time.sleep(delay)

        return all_messages

    def delete(self, count: int):
        id = self.get_id(count)
        data = {"ids": [id]}
        post = api().action("DELETE_KIDNOTE_V1_NOTE", data, self.acc)
        code = post["statusCode"]
        if code == -500:
            print("删除失败")
            return False
        elif code == 200:
            print("删除成功：")
            return True
        else:
            print("unknown error:")
            print(post)
