# -*- coding: utf-8 -*-
"""
希沃班牌机器人 TUI 客户端
基于 Textual 的终端交互界面
"""

import os
import json
import asyncio
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Input, ListView, ListItem
from textual.reactive import reactive
from textual.message import Message

# 加载配置
CONFIG_FILE = "config.json"
def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

config = load_config()
API_KEY = config.get("api_key", "your-secret-key")
API_URL = f"http://localhost:{config.get('api_port', 5000)}"


class MessageWidget(Static):
    """消息显示组件"""
    def __init__(self, msg_data: dict):
        self.msg_data = msg_data
        self.sender = msg_data.get("sender", "unknown")
        super().__init__()

    def compose(self) -> ComposeResult:
        time_str = self.msg_data.get("time", "")
        content = self.msg_data.get("content", "")
        sender_name = self.msg_data.get("senderName", "未知")
        msg_type = self.msg_data.get("type", 1)

        # 格式化显示
        type_map = {0: "[TXT]", 1: "[TXT]", 2: "[IMG]", 3: "[AUD]", 4: "[VID]", 5: "[FILE]", 6: "[RICH]"}
        type_icon = type_map.get(int(msg_type), "[MSG]")

        # 处理空内容（图片/音频等）
        if not content and self.msg_data.get("resUrl"):
            content = "[媒体文件]"

        yield Static(f"[{time_str}] {type_icon} {sender_name}: {content}")

    def on_mount(self) -> None:
        """根据发送者设置样式"""
        if self.sender == "parent":
            self.add_class("msg-parent")
        elif self.sender == "student":
            self.add_class("msg-student")


class StatusWidget(Static):
    """状态显示组件"""
    status = reactive("未连接")

    def watch_status(self, status: str):
        self.update(f"状态: {status}")


class SeewoTUI(App):
    """希沃班牌机器人 TUI 应用"""

    CSS = """
    Screen {
        layout: vertical;
    }

    .message-list {
        height: 65%;
        overflow-y: scroll;
        border: solid $primary;
        padding: 1;
    }

    .input-area {
        height: 10%;
        layout: horizontal;
        border: solid $secondary;
    }

    .button-area {
        height: 10%;
        layout: horizontal;
        align: center middle;
    }

    .status-bar {
        height: 5%;
        content-align: center middle;
        background: $primary;
        color: $text;
    }

    /* 家长消息靠右 */
    .msg-parent {
        margin: 1;
        padding: 1;
        background: $primary-lighten-2;
        text-align: right;
        color: $text;
    }

    /* 学生消息靠左 */
    .msg-student {
        margin: 1;
        padding: 1;
        background: $secondary-lighten-2;
        text-align: left;
        color: $text;
    }

    Input {
        width: 80%;
    }

    Button {
        width: 15%;
        margin: 1;
    }

    .sync-btn {
        background: $warning;
    }

    .load-btn {
        background: $success;
    }
    """

    BINDINGS = [
        ("q", "quit", "退出"),
        ("r", "refresh", "刷新"),
        ("s", "send", "发送"),
        ("h", "history", "历史"),
        ("l", "load_earlier", "加载更早"),
        ("y", "sync_all", "全量同步"),
        ("i", "image", "图片"),
        ("a", "audio", "音频"),
    ]

    messages = reactive([])
    status_text = reactive("未连接")
    has_more = reactive(True)  # 是否还有更早的消息

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("消息列表", classes="status-bar"),
            Container(id="message-list", classes="message-list"),
            Horizontal(
                Input(placeholder="输入消息内容...", id="msg-input"),
                Button("发送", id="send-btn"),
                classes="input-area"
            ),
            Horizontal(
                Button("加载更早", id="load-btn", classes="load-btn"),
                Button("全量同步", id="sync-btn", classes="sync-btn"),
                classes="button-area"
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """应用启动时初始化"""
        self.title = "希沃班牌机器人"
        asyncio.create_task(self.check_connection())
        asyncio.create_task(self.load_messages())

    async def check_connection(self) -> None:
        """检查API连接状态"""
        try:
            import requests
            resp = requests.get(f"{API_URL}/api/status", headers={"X-API-Key": API_KEY}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                student = data.get("student", {})
                self.status_text = f"已连接 - 学生: {student.get('name', 'unknown')}"
            else:
                self.status_text = "连接失败"
        except Exception as e:
            self.status_text = f"连接错误: {str(e)[:20]}"

    async def load_messages(self) -> None:
        """加载消息列表"""
        try:
            import requests
            resp = requests.get(f"{API_URL}/api/messages?count=20", headers={"X-API-Key": API_KEY}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.messages = data.get("messages", [])
                self.render_messages()
        except Exception as e:
            self.query_one("#message-list").mount(Static(f"加载失败: {e}"))

    async def load_history(self) -> None:
        """加载本地历史记录"""
        try:
            import requests
            resp = requests.get(f"{API_URL}/api/history?limit=100", headers={"X-API-Key": API_KEY}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.messages = data.get("messages", [])
                self.has_more = data.get("earliest_id", 0) > 0  # 如果 earliest_id > 0，可能还有更早的
                self.render_messages()
        except Exception as e:
            self.query_one("#message-list").mount(Static(f"加载失败: {e}"))

    async def load_earlier_messages(self) -> None:
        """加载更早的消息（滚动加载）"""
        if not self.has_more:
            self.query_one("#message-list").mount(Static("已到达最早消息"))
            return

        try:
            import requests
            resp = requests.get(f"{API_URL}/api/load_earlier?count=50", headers={"X-API-Key": API_KEY}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                new_msgs = data.get("messages", [])
                self.has_more = data.get("has_more", False)

                if new_msgs:
                    # 插入到开头
                    self.messages = new_msgs + self.messages
                    self.render_messages(scroll_to_top=True)
                else:
                    self.query_one("#message-list").mount(Static("已到达最早消息"))
            else:
                self.query_one("#message-list").mount(Static(f"加载失败: {resp.text}"))
        except Exception as e:
            self.query_one("#message-list").mount(Static(f"加载错误: {e}"))

    async def sync_all_messages(self) -> None:
        """全量同步所有历史消息"""
        self.query_one("#message-list").mount(Static("正在全量同步，请稍候..."))

        try:
            import requests
            resp = requests.post(
                f"{API_URL}/api/sync_all",
                headers={"X-API-Key": API_KEY},
                json={"batch_size": 50, "delay": 2.0},
                timeout=300  # 5分钟超时
            )
            if resp.status_code == 200:
                data = resp.json()
                synced_count = data.get("synced_count", 0)
                total_count = data.get("total_count", 0)
                self.query_one("#message-list").mount(Static(f"同步完成: 新增 {synced_count} 条，共 {total_count} 条"))
                await self.load_history()  # 重新加载历史
            else:
                self.query_one("#message-list").mount(Static(f"同步失败: {resp.text}"))
        except Exception as e:
            self.query_one("#message-list").mount(Static(f"同步错误: {e}"))

    def render_messages(self, scroll_to_top: bool = False) -> None:
        """渲染消息列表"""
        container = self.query_one("#message-list")
        container.remove_children()

        if not self.messages:
            container.mount(Static("暂无消息"))
            return

        # API返回顺序已是旧→新，直接按顺序显示（旧消息在上面）
        for msg in self.messages:
            container.mount(MessageWidget(msg))

        # 滚动到指定位置
        if scroll_to_top:
            container.scroll_home(animate=False)
        else:
            container.scroll_end(animate=False)

    async def send_message(self, content: str) -> None:
        """发送消息"""
        if not content:
            return

        try:
            import requests
            resp = requests.post(
                f"{API_URL}/api/send",
                headers={"X-API-Key": API_KEY},
                json={"content": content},
                timeout=5
            )
            if resp.status_code == 200:
                self.query_one("#msg-input").value = ""
                await self.load_messages()
            else:
                self.query_one("#message-list").mount(Static(f"发送失败: {resp.text}"))
        except Exception as e:
            self.query_one("#message-list").mount(Static(f"发送错误: {e}"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """按钮点击事件"""
        if event.button.id == "send-btn":
            content = self.query_one("#msg-input").value
            asyncio.create_task(self.send_message(content))
        elif event.button.id == "load-btn":
            asyncio.create_task(self.load_earlier_messages())
        elif event.button.id == "sync-btn":
            asyncio.create_task(self.sync_all_messages())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """输入提交事件"""
        if event.input.id == "msg-input":
            asyncio.create_task(self.send_message(event.value))

    def action_refresh(self) -> None:
        """刷新消息"""
        asyncio.create_task(self.load_messages())

    def action_history(self) -> None:
        """查看历史记录"""
        asyncio.create_task(self.load_history())

    def action_load_earlier(self) -> None:
        """加载更早消息"""
        asyncio.create_task(self.load_earlier_messages())

    def action_sync_all(self) -> None:
        """全量同步"""
        asyncio.create_task(self.sync_all_messages())

    def action_send(self) -> None:
        """发送消息"""
        content = self.query_one("#msg-input").value
        asyncio.create_task(self.send_message(content))

    def action_image(self) -> None:
        """发送图片"""
        self.query_one("#message-list").mount(Static("提示: python client.py image <文件路径>"))

    def action_audio(self) -> None:
        """发送音频"""
        self.query_one("#message-list").mount(Static("提示: python client.py audio <文件路径>"))


if __name__ == "__main__":
    app = SeewoTUI()
    app.run()