# Seewo 班牌机器人

## 介绍
Seewo 班牌机器人是一个用于「希沃云班」微信小程序或「希沃魔方」APP的聊天机器人
## 功能
该程序利用「希沃统一服务平台」的相关API实现「希沃云班」的「亲情留言」以及相关功能，已实现的有：
- 微信二维码登录
- 留言接收
- 留言发送
## 使用
1. 确保你已添加至少一个学校和学生，并拥有**完整**Python **3.x**的环境。
2. 若没有**Requests**和**numpy**库，则运行：

```
pip3 install requests np
```
3. 运行主程序：

```
python3 auto.py
```
4. 首次运行会出现二维码，必须使用**微信扫码**登录。
5. 若程序正常运行，将会输出最新留言消息。

## API相关说明
详见[Seewo-API](https://github.com/cmy2008/api-collet/blob/main/seewo/readme.md)
