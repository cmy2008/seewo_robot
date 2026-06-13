# -*- coding: utf-8 -*-
"""
希沃班牌机器人 API 客户端
"""

import os
import json
import requests
from typing import Optional

# 加载配置
CONFIG_FILE = "config.json"


def load_config() -> dict:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


_config = load_config()
DEFAULT_API_KEY = _config.get("api_key", "your-secret-key")
DEFAULT_API_URL = f"http://localhost:{_config.get('api_port', 5000)}"


class SeewoClient:
    """希沃班牌机器人客户端"""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or DEFAULT_API_URL).rstrip("/")
        self.api_key = api_key or DEFAULT_API_KEY
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        return response.json()

    def get_status(self) -> dict:
        """获取服务状态"""
        return self._request("GET", "/api/status")

    def get_messages(self, count: int = 10) -> dict:
        """获取消息列表"""
        return self._request("GET", "/api/messages", params={"count": count})

    def send_text(self, content: str) -> dict:
        """发送文本消息"""
        return self._request("POST", "/api/send", json={"content": content})

    def send_image(
        self,
        file_path: str = None,
        file_data: bytes = None,
        filename: str = "image.png",
    ) -> dict:
        """发送图片

        Args:
            file_path: 本地文件路径
            file_data: 文件二进制数据（与file_path二选一）
            filename: 文件名
        """
        if file_path:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "image/png")}
                return self._request("POST", "/api/send_image", files=files)
        elif file_data:
            files = {"file": (filename, file_data, "image/png")}
            return self._request("POST", "/api/send_image", files=files)
        else:
            raise ValueError("file_path or file_data is required")

    def send_audio(self, file_path: str, voice_length: int = 666) -> dict:
        """发送音频

        Args:
            file_path: 音频文件路径
            voice_length: 音频时长(毫秒)
        """
        return self._request(
            "POST",
            "/api/send_audio",
            json={"file_path": file_path, "voice_length": voice_length},
        )

    def get_history(self, limit: int = 50, offset: int = 0) -> dict:
        """获取聊天记录"""
        return self._request(
            "GET", "/api/history", params={"limit": limit, "offset": offset}
        )

    def refresh_session(self) -> dict:
        """刷新会话"""
        return self._request("POST", "/api/refresh")

    def execute_command(self, command: str) -> dict:
        """执行命令"""
        return self._request("POST", "/api/execute", json={"command": command})


# 命令行接口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="希沃班牌机器人客户端")
    parser.add_argument("--url", default=None, help="API服务地址")
    parser.add_argument("--key", default=None, help="API密钥")

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # status
    subparsers.add_parser("status", help="获取服务状态")

    # messages
    msg_parser = subparsers.add_parser("messages", help="获取消息列表")
    msg_parser.add_argument("--count", type=int, default=10, help="获取数量")

    # send
    send_parser = subparsers.add_parser("send", help="发送文本消息")
    send_parser.add_argument("content", help="消息内容")

    # image
    img_parser = subparsers.add_parser("image", help="发送图片")
    img_parser.add_argument("file", help="图片文件路径")

    # audio
    audio_parser = subparsers.add_parser("audio", help="发送音频")
    audio_parser.add_argument("file", help="音频文件路径")
    audio_parser.add_argument("--length", type=int, default=666, help="音频时长(毫秒)")

    # history
    hist_parser = subparsers.add_parser("history", help="获取聊天记录")
    hist_parser.add_argument("--limit", type=int, default=50, help="返回条数")
    hist_parser.add_argument("--offset", type=int, default=0, help="偏移量")

    # refresh
    subparsers.add_parser("refresh", help="刷新会话")

    args = parser.parse_args()

    client = SeewoClient(base_url=args.url, api_key=args.key)

    if args.command == "status":
        result = client.get_status()
    elif args.command == "messages":
        result = client.get_messages(count=args.count)
    elif args.command == "send":
        result = client.send_text(args.content)
    elif args.command == "image":
        result = client.send_image(file_path=args.file)
    elif args.command == "audio":
        result = client.send_audio(file_path=args.file, voice_length=args.length)
    elif args.command == "history":
        result = client.get_history(limit=args.limit, offset=args.offset)
    elif args.command == "refresh":
        result = client.refresh_session()
    else:
        parser.print_help()
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
