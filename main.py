# -*- coding: utf-8 -*-

# TODO: 多学生选择
import os
import time
import json

os.chdir(os.path.dirname(__file__))
print("当前路径：" + os.getcwd())

from init import *
from login import *
from funcs import *
from stu import *
from msg import *
from upload import *
from yunban import *

# 加载配置
CONFIG_FILE = "config.json"
def load_config() -> dict:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()
POLL_BATCH_SIZE = config.get("poll_batch_size", 50)
BASE_INTERVAL = config.get("base_interval", 1)
MAX_INTERVAL = config.get("max_interval", 10)
MAX_ERRORS = config.get("max_errors", 5)

account = acc()
student = stu(account)
stu_msg = msg(account, student)


def upload_file(account: acc, file, type="image/png"):
    up = Upload(account)
    up.upload(file=file, type=type)
    return up.downloadUrl


def send_msg(send: str):
    try:
        # TODO: 超时处理
        print(send)
        if len(send) > 199:
            send = send[:196] + "..."
            logw("[WARN] 消息过长，已截断")
        stu_msg.send(send, 1)
    except Exception as e:
        log = f"[ERROR] 发送失败: {e}"
        logw(log)


def send_audio(file):
    try:
        stu_msg.send(os.path.basename(file), 1)
        url = upload_file(account, file)
        if url:
            stu_msg.send('', 3, url, 666)
        else:
            send_msg(f"[ERROR] 文件上传失败: {file}")
    except Exception as e:
        send_msg(f"[ERROR] 发送音频失败: {e}")


def handle_command(command_text: str):
    """处理以/开头的命令"""
    args = command_text.split(' ')
    match args[0]:
        case "getpass":
            if len(args) >= 3:
                send_msg(str(getpass(account, student.schoolUid, args[1], args[2])))
            else:
                send_msg("[ERROR] 用法: /getpass <schoolUid> <snCode>")
        case "发送音乐":
            if not os.path.exists("music"):
                os.mkdir("music")
            filelist = os.listdir("music")
            if not filelist:
                send_msg("[INFO] music 目录为空")
            for file in filelist:
                send_audio("music/" + file)
        case _:
            send_msg(os.popen(command_text).read())


def reconnect():
    """重新登录并刷新全局对象"""
    global account, student, stu_msg
    logw("[INFO] 正在重新登录...")
    account = acc(type=1)
    student = stu(account)
    stu_msg = msg(account, student)
    logw("[INFO] 重新登录成功")


def main():
    # 加载历史聊天记录
    history = load_chat_history()
    msg_id = history.get("last_id", 0)
    earliest_id = history.get("earliest_id", 0)
    total_msgs = len(history.get("messages", []))

    print(f"已加载聊天记录，最后消息ID: {msg_id}，最早消息ID: {earliest_id}，共 {total_msgs} 条")

    # 快速启动：只获取最近100条消息（如果本地没有记录）
    if total_msgs == 0:
        print("首次运行，正在获取最近100条消息...")
        try:
            # 直接获取 result，按时间倒序（新→旧）
            result = stu_msg.get(100).get("result", [])
            # 按倒序处理（新→旧），第一条就是最新消息
            for msg in result:
                mid = int(msg.get("id", 0))  # 确保 ID 是整数
                content = msg.get("content", "")
                msg_type = msg.get("type", 1)
                sender = msg.get("senderType", "unknown")
                append_message(mid, content, str(msg_type), sender)
            history = load_chat_history()
            print(f"获取完成，共 {len(history.get('messages', []))} 条")
            msg_id = history.get("last_id", 0)
            earliest_id = history.get("earliest_id", 0)
        except Exception as err:
            logw(f"[ERROR] 获取历史消息失败: {err}")

    last_msg = ' '
    consecutive_errors = 0
    current_interval = BASE_INTERVAL

    while True:
        time.sleep(current_interval)

        try:
            # 直接获取 result，按时间倒序（新→旧）
            result = stu_msg.get(POLL_BATCH_SIZE).get("result", [])
            consecutive_errors = 0
        except Exception as err:
            consecutive_errors += 1
            log = f"[ERROR] 获取消息失败({consecutive_errors}/{MAX_ERRORS}): {err}"
            logw(log)
            if consecutive_errors >= MAX_ERRORS:
                try:
                    reconnect()
                    consecutive_errors = 0
                except Exception as e:
                    logw(f"[ERROR] 重连失败: {e}")
            continue

        # 提取所有消息ID（倒序：新→旧），确保是整数
        all_ids = [int(m.get("id", 0)) for m in result]
        # 筛选出未读的新消息ID
        new_ids = [mid for mid in all_ids if mid > msg_id]

        if not new_ids:
            last_msg = " "
            # 无新消息时逐步增加轮询间隔
            current_interval = min(current_interval + 0.5, MAX_INTERVAL)
            continue

        # 有新消息，重置轮询间隔
        current_interval = BASE_INTERVAL

        # 逐条处理新消息（从旧到新）
        # 反转 new_ids 使其按时间正序（旧→新）
        for mid in reversed(new_ids):
            try:
                # 在 result 中找到对应的消息
                msg = next((m for m in result if m.get("id") == mid), None)
                if not msg:
                    continue
                last_msg = msg.get("content", "")
                msg_type = msg.get("type", 1)
                sender = msg.get("senderType", "unknown")
                msg_id = mid

                # 保存到聊天记录
                append_message(mid, last_msg, str(msg_type), sender)

            except Exception as err:
                log = f"[ERROR] 消息获取失败(id={mid}): {err}"
                logw(log)
                msg_id = mid
                continue

            logw(last_msg)
            print(datenow() + last_msg)

            # 处理命令
            if last_msg and last_msg[0] == "/":
                handle_command(last_msg[1:])


if __name__ == "__main__":
    main()
