# -*- coding: utf-8 -*-

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
    with open(file, "r",encoding='utf-8') as f:
        content = f.read()
        return content

def write_file(file: str, data: bytes) -> bool:
    with open(file, "wb") as f:
        f.write(data)
    return True

def load_json(file: str) -> dict:
    return json.loads(read_file(file))


def datenow() -> str:
    return '[' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ']: '

def logw(t: str) -> None:
    global filedate
    log=datenow() + t + '\n'
    log_dir='logs/'
    dirc=log_dir + filedate + '.log'
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    with open(dirc, 'a') as file:
        file.write(log)


# 聊天记录存储
CHAT_LOG_FILE = "chat_history.json"

def load_chat_history() -> dict:
    """加载聊天记录，返回 {last_id: int, earliest_id: int, messages: list}"""
    if os.path.exists(CHAT_LOG_FILE):
        try:
            data = load_json(CHAT_LOG_FILE)
            # 确保 earliest_id 存在
            if "earliest_id" not in data:
                if data.get("messages"):
                    data["earliest_id"] = min(m["id"] for m in data["messages"])
                else:
                    data["earliest_id"] = 0
            return data
        except (json.JSONDecodeError, KeyError):
            pass
    return {"last_id": 0, "earliest_id": 0, "messages": []}


def save_chat_history(history: dict) -> None:
    """保存聊天记录"""
    with open(CHAT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def append_message(msg_id: int, content: str, msg_type: str = "text", sender: str = "") -> None:
    """追加一条消息到聊天记录
    
    注意：消息会按ID排序，确保顺序正确（旧→新）
    """
    history = load_chat_history()
    
    # 添加新消息
    new_msg = {
        "id": msg_id,
        "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        "content": content,
        "type": msg_type,
        "sender": sender
    }
    history["messages"].append(new_msg)
    
    # 按ID排序（旧→新）
    history["messages"] = sorted(history["messages"], key=lambda m: m["id"])
    
    # 更新 last_id 为最大ID
    if history["messages"]:
        history["last_id"] = max(m["id"] for m in history["messages"])
        history["earliest_id"] = min(m["id"] for m in history["messages"])
    
    save_chat_history(history)


def prepend_messages(messages: list) -> None:
    """在聊天记录开头插入历史消息（用于加载更早的消息）"""
    if not messages:
        return
    history = load_chat_history()
    # 插入到开头
    history["messages"] = messages + history["messages"]
    # 更新最早消息ID
    min_id = min(m["id"] for m in messages)
    if history["earliest_id"] == 0 or min_id < history["earliest_id"]:
        history["earliest_id"] = min_id
    save_chat_history(history)


def update_earliest_id(msg_id: int) -> None:
    """更新最早消息ID"""
    history = load_chat_history()
    if history["earliest_id"] == 0 or msg_id < history["earliest_id"]:
        history["earliest_id"] = msg_id
        save_chat_history(history)