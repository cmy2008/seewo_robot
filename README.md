# Seewo 班牌机器人
> [!WARNING]
> ## 该项目正在开发中，请勿用于学习环境，否则可能会带来严重后果！

## 介绍
Seewo 班牌机器人是一个用于「希沃云班」微信小程序或「希沃魔方」APP的聊天机器人

## 功能
该程序利用「希沃统一服务平台」的相关API实现「希沃云班」的「亲情留言」以及相关功能，已实现的有：
- 微信二维码登录
- 留言接收与实时显示
- 留言发送（文本/图片/音频）
- 命令执行（以"/"开头的留言）
- REST API 服务端
- TUI 终端客户端
- 聊天记录持久化
- 按需加载历史消息
- 全量同步功能（防风控）

## 安装依赖

```bash
# 核心依赖（必需）
pip install requests numpy pillow requests-toolbelt

# API 服务端依赖（可选，不装则无法运行api_server.py）
pip install flask

# TUI 客户端依赖（可选, 不装则无法运行tui_client.py）
pip install textual

# 或一键安装全部依赖
pip install -r requirements.txt
```

## 使用方式

### 方式1：主程序（消息监听）

```bash
python main.py
```

首次运行会出现二维码，必须使用**微信扫码**登录。程序会实时输出最新留言消息。

### 方式2：API 服务端 + TUI 客户端

```bash
# 1. 启动 API 服务端
python api_server.py

# 2. 启动 TUI 客户端
python tui_client.py
```

**TUI 快捷键：**
| 键 | 功能 |
|----|------|
| `R` | 刷新消息 |
| `H` | 查看本地历史 |
| `L` | 加载更早消息 |
| `Y` | 全量同步 |
| `S` | 发送消息 |
| `Q` | 退出 |

### 方式3：命令行客户端

```bash
python client.py status          # 查看状态
python client.py messages        # 获取消息列表
python client.py send "你好"     # 发送消息
python client.py image photo.png # 发送图片
python client.py audio music.mp3 # 发送音频
python client.py history         # 查看本地历史
```

### 方式4：快速发送消息

```bash
python send_msg.py "今天放学早点回来"
```

## 配置文件

`config.json` 配置说明：

```json
{
  "api_key": "your-secret-key",    // API 密钥
  "api_port": 5001,                // API 服务端口
  "api_host": "0.0.0.0",           // API 服务主机
  "poll_batch_size": 50,           // 每次轮询消息数量
  "base_interval": 1,              // 基础轮询间隔(秒)
  "max_interval": 10,              // 最大轮询间隔(秒)
  "max_errors": 5                  // 连续错误上限
}
```

## API 接口

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/status` | GET | 获取服务状态 |
| `/api/messages` | GET | 获取消息列表 |
| `/api/send` | POST | 发送文本消息 |
| `/api/send_image` | POST | 发送图片 |
| `/api/send_audio` | POST | 发送音频 |
| `/api/history` | GET | 获取本地聊天记录 |
| `/api/load_earlier` | GET | 加载更早的消息 |
| `/api/sync_all` | POST | 全量同步所有历史 |
| `/api/refresh` | POST | 刷新会话 |

所有接口需要 `X-API-Key` header 认证。

## 数据文件

| 文件 | 说明 |
|------|------|
| `tokens.json` | 登录 Token 存储 |
| `chat_history.json` | 聊天记录持久化 |
| `config.json` | 配置文件 |
| `logs/*.log` | 按日期记录日志 |

## 命令示例

当收到以 `/` 开头的消息时，会执行命令：

| 命令 | 功能 |
|------|------|
| `/getpass <schoolUid> <snCode>` | 获取离线验证码 |
| `/发送音乐` | 发送 music/ 目录下的音频 |

## 项目结构

```
seewo_robot/
├── main.py          # 主程序（消息监听）
├── api_server.py    # REST API 服务端
├── tui_client.py    # TUI 终端客户端
├── client.py        # Python SDK + 命令行客户端
├── send_msg.py      # 快速发送消息脚本
├── login.py         # 登录模块
├── msg.py           # 消息收发模块
├── stu.py           # 学生信息管理
├── upload.py        # 文件上传模块
├── funcs.py         # 工具函数
├── init.py          # 初始化配置
├── yunban.py        # 云班功能扩展
├── config.json      # 配置文件
└── README.md        # 说明文档
```

## API相关说明
详见[Seewo-API](https://github.com/cmy2008/api-collet/blob/main/seewo/readme.md)