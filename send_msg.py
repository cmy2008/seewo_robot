# -*- coding: utf-8 -*-
"""发送指定消息到班牌"""

import sys
from login import acc
from stu import stu
from msg import msg


def main():
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: python send_msg.py <消息内容>")
        print("示例: python send_msg.py 你好，这是家长的测试消息")
        sys.exit(1)

    message = sys.argv[1]

    # 登录并获取学生信息
    print("正在登录...")
    account = acc()
    student = stu(account)
    stu_msg = msg(account, student)

    print(f"学生信息: 学校={student.schoolUid}, 班级={student.classUid}")

    # 发送消息
    print(f"正在发送消息: {message}")
    result = stu_msg.send(message, 1)

    if result:
        print("✅ 发送成功")
    else:
        print("❌ 发送失败")


if __name__ == "__main__":
    main()