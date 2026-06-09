# -*- coding: utf-8 -*-
"""
希沃班牌机器人 API 服务端
提供 REST API 接口供客户端调用
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from functools import wraps

os.chdir(os.path.dirname(__file__))

from init import *
from login import *
from funcs import *
from stu import *
from msg import *
from upload import *
from yunban import *

app = Flask(__name__)

# 加载配置
CONFIG_FILE = "config.json"
def load_config() -> dict:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()
API_KEY = config.get("api_key", "your-secret-key")
API_PORT = config.get("api_port", 5000)
API_HOST = config.get("api_host", "0.0.0.0")


def require_api_key(f):
    """API密钥验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized", "message": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated


# 全局会话对象
class Session:
    def __init__(self):
        self.account = None
        self.student = None
        self.stu_msg = None
        self._initialized = False

    def init(self):
        """初始化会话"""
        if not self._initialized:
            self.account = acc()
            self.student = stu(self.account)
            self.stu_msg = msg(self.account, self.student)
            self._initialized = True
        return self

    def refresh(self):
        """刷新会话"""
        self._initialized = False
        return self.init()


session = Session()


def upload_file_to_cloud(file_path: str, content_type: str = "image/png") -> str:
    """上传文件到云存储"""
    up = Upload(session.account)
    up.upload(file=file_path, type=content_type)
    return up.downloadUrl


# ============== API 路由 ==============

@app.route("/api/status", methods=["GET"])
@require_api_key
def get_status():
    """获取服务状态"""
    try:
        session.init()
        return jsonify({
            "status": "ok",
            "student": {
                "name": getattr(session.student, "name", "unknown"),
                "schoolUid": getattr(session.student, "schoolUid", ""),
                "classUid": getattr(session.student, "classUid", ""),
                "userUid": getattr(session.student, "userUid", "")
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/messages", methods=["GET"])
@require_api_key
def get_messages():
    """获取消息列表

    Query params:
        count: 获取数量，默认10
    """
    try:
        session.init()
        count = int(request.args.get("count", 10))
        result = session.stu_msg.get(count)
        raw_messages = result.get("result", [])

        # 格式化消息数据
        messages = []
        parent_uid = session.account.uid
        student_uid = session.student.userUid

        for msg in raw_messages:
            # 解析时间
            create_time = msg.get("createTime", 0)
            if create_time:
                from datetime import datetime
                time_str = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = ""

            # 判断发送者
            sender_uid = msg.get("senderUid", "")
            if sender_uid == parent_uid:
                sender = "parent"
                sender_name = "家长"
            elif sender_uid == student_uid:
                sender = "student"
                sender_name = session.student.name
            else:
                sender = "unknown"
                sender_name = msg.get("senderName", "未知")

            messages.append({
                "id": msg.get("id", 0),
                "time": time_str,
                "content": msg.get("content", ""),
                "type": msg.get("type", 1),
                "sender": sender,
                "senderName": sender_name,
                "resUrl": msg.get("resUrl", "")
            })

        return jsonify({
            "status": "ok",
            "count": len(messages),
            "messages": messages
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/send", methods=["POST"])
@require_api_key
def send_message():
    """发送文本消息

    JSON body:
        content: 消息内容
    """
    try:
        session.init()
        data = request.get_json()
        content = data.get("content", "")

        if not content:
            return jsonify({"status": "error", "message": "content is required"}), 400

        if len(content) > 199:
            content = content[:196] + "..."

        success = session.stu_msg.send(content, 1)
        return jsonify({
            "status": "ok" if success else "error",
            "message": "发送成功" if success else "发送失败"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/send_image", methods=["POST"])
@require_api_key
def send_image():
    """发送图片

    JSON body:
        file_path: 图片文件路径
    或 multipart/form-data:
        file: 图片文件
    """
    try:
        session.init()

        # 方式1: JSON body 传文件路径
        if request.is_json:
            data = request.get_json()
            file_path = data.get("file_path")
            if not file_path or not os.path.exists(file_path):
                return jsonify({"status": "error", "message": "file_path invalid"}), 400
        # 方式2: 上传文件
        else:
            if "file" not in request.files:
                return jsonify({"status": "error", "message": "no file uploaded"}), 400
            file = request.files["file"]
            file_path = f"temp_{file.filename}"
            file.save(file_path)

        # 上传并发送
        url = upload_file_to_cloud(file_path, "image/png")
        if url:
            session.stu_msg.send("", 2, url)
            return jsonify({"status": "ok", "url": url})
        else:
            return jsonify({"status": "error", "message": "upload failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/send_audio", methods=["POST"])
@require_api_key
def send_audio():
    """发送音频

    JSON body:
        file_path: 音频文件路径
        voice_length: 音频时长(毫秒)，默认666
    """
    try:
        session.init()
        data = request.get_json()
        file_path = data.get("file_path")
        voice_length = data.get("voice_length", 666)

        if not file_path or not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "file_path invalid"}), 400

        # 发送文件名
        session.stu_msg.send(os.path.basename(file_path), 1)

        # 上传并发送音频
        url = upload_file_to_cloud(file_path, "audio/mp3")
        if url:
            session.stu_msg.send("", 3, url, voice_length)
            return jsonify({"status": "ok", "url": url})
        else:
            return jsonify({"status": "error", "message": "upload failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/history", methods=["GET"])
@require_api_key
def get_history():
    """获取本地聊天记录

    Query params:
        limit: 返回条数，默认50
        offset: 偏移量，默认0
    """
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        history = load_chat_history()
        messages = history.get("messages", [])

        # 分页
        total = len(messages)
        messages = messages[offset:offset + limit]

        return jsonify({
            "status": "ok",
            "total": total,
            "earliest_id": history.get("earliest_id", 0),
            "last_id": history.get("last_id", 0),
            "count": len(messages),
            "messages": messages
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/load_earlier", methods=["GET"])
@require_api_key
def load_earlier_messages():
    """加载更早的消息（滚动加载历史）

    Query params:
        count: 获取数量，默认50
    """
    try:
        session.init()
        count = int(request.args.get("count", 50))

        history = load_chat_history()
        earliest_id = history.get("earliest_id", 0)

        # 如果 earliest_id 为 0，说明没有记录
        if earliest_id == 0:
            return jsonify({"status": "error", "message": "no messages in history"}), 400

        # 获取更早的消息
        earlier_msgs = session.stu_msg.get_earlier_messages(earliest_id, count)

        if not earlier_msgs:
            return jsonify({
                "status": "ok",
                "message": "已到达最早消息",
                "has_more": False,
                "count": 0,
                "messages": []
            })

        # 格式化并保存到本地
        parent_uid = session.account.uid
        student_uid = session.student.userUid
        formatted_msgs = []

        for msg in earlier_msgs:
            # 解析时间
            create_time = msg.get("createTime", 0)
            if create_time:
                from datetime import datetime
                time_str = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = ""

            # 判断发送者
            sender_uid = msg.get("senderUid", "")
            if sender_uid == parent_uid:
                sender = "parent"
                sender_name = "家长"
            elif sender_uid == student_uid:
                sender = "student"
                sender_name = session.student.name
            else:
                sender = "unknown"
                sender_name = msg.get("senderName", "未知")

            formatted_msg = {
                "id": msg.get("id", 0),
                "time": time_str,
                "content": msg.get("content", ""),
                "type": msg.get("type", 1),
                "sender": sender,
                "senderName": sender_name,
                "resUrl": msg.get("resUrl", "")
            }
            formatted_msgs.append(formatted_msg)

        # 插入到本地历史开头
        prepend_messages(formatted_msgs)

        # 判断是否还有更早的消息
        has_more = len(earlier_msgs) >= count

        return jsonify({
            "status": "ok",
            "has_more": has_more,
            "count": len(formatted_msgs),
            "messages": formatted_msgs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/sync_all", methods=["POST"])
@require_api_key
def sync_all_messages():
    """全量同步所有历史消息（后台执行，耗时较长）

    JSON body:
        batch_size: 每次获取数量，默认50
        delay: 每次请求间隔(秒)，默认2.0（防风控）
    """
    try:
        session.init()
        data = request.get_json() or {}
        batch_size = data.get("batch_size", 50)
        delay = data.get("delay", 2.0)

        history = load_chat_history()
        earliest_id = history.get("earliest_id", 0)

        # 如果没有记录，从最新消息开始
        if earliest_id == 0:
            latest_msgs = session.stu_msg.get(100).get("result", [])
            if latest_msgs:
                earliest_id = min(m.get("id", 0) for m in latest_msgs)

        # 获取所有历史消息
        all_msgs = session.stu_msg.get_all_messages_until_earliest(earliest_id, batch_size, delay)

        # 格式化并保存
        parent_uid = session.account.uid
        student_uid = session.student.userUid
        formatted_msgs = []

        for msg in all_msgs:
            create_time = msg.get("createTime", 0)
            if create_time:
                from datetime import datetime
                time_str = datetime.fromtimestamp(create_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = ""

            sender_uid = msg.get("senderUid", "")
            if sender_uid == parent_uid:
                sender = "parent"
                sender_name = "家长"
            elif sender_uid == student_uid:
                sender = "student"
                sender_name = session.student.name
            else:
                sender = "unknown"
                sender_name = msg.get("senderName", "未知")

            formatted_msg = {
                "id": msg.get("id", 0),
                "time": time_str,
                "content": msg.get("content", ""),
                "type": msg.get("type", 1),
                "sender": sender,
                "senderName": sender_name,
                "resUrl": msg.get("resUrl", "")
            }
            formatted_msgs.append(formatted_msg)

        # 插入到本地历史开头
        prepend_messages(formatted_msgs)

        # 更新 earliest_id
        if formatted_msgs:
            update_earliest_id(min(m["id"] for m in formatted_msgs))

        return jsonify({
            "status": "ok",
            "message": "全量同步完成",
            "synced_count": len(formatted_msgs),
            "total_count": len(load_chat_history().get("messages", []))
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/refresh", methods=["POST"])
@require_api_key
def refresh_session():
    """刷新会话（重新登录）"""
    try:
        session.refresh()
        return jsonify({"status": "ok", "message": "会话已刷新"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/execute", methods=["POST"])
@require_api_key
def execute_command():
    """执行命令（慎用）

    JSON body:
        command: 命令内容
    """
    try:
        session.init()
        data = request.get_json()
        command = data.get("command", "")

        if not command:
            return jsonify({"status": "error", "message": "command is required"}), 400

        # 安全限制：只允许特定命令
        allowed_prefixes = ["getpass", "发送音乐"]
        if not any(command.startswith(p) for p in allowed_prefixes):
            return jsonify({"status": "error", "message": "command not allowed"}), 403

        result = os.popen(command).read()
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("希沃班牌机器人 API 服务")
    print("=" * 50)
    print(f"API Key: {API_KEY}")
    print(f"端口: {API_PORT}")
    print(f"主机: {API_HOST}")
    print("=" * 50)

    app.run(host=API_HOST, port=API_PORT, debug=False)