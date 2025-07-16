# 项目简介

本项目是一个基于 Flask 和 Flask-SocketIO 的简易聊天室，支持用户登录、实时消息广播、在线用户列表显示及消息历史保存。

## 功能特性

- 用户登录与登出（密码为 `kawaimiku`）
- 实时聊天，消息自动广播给所有在线用户
- 在线用户状态显示
- 聊天消息历史保存（最多100条，存储于 `chat_history.json`）
- 消息长度限制（最多500字符）

## 安装与运行

### 安装依赖：
```bash
pip install flask flask-socketio markupsafe
```

### 启动服务：
```bash
python app.py
```

启动后访问 [http://localhost:11451](http://localhost:11451)

## 主要文件说明

- `app.py`：主程序入口，包含所有后端逻辑
- `chat_history.json`：消息历史存储文件
- `templates/`：前端页面模板（需包含 `login.html` 和 `chat.html`）

## 使用方法

1. 打开浏览器访问主页，输入用户名和密码（密码为 `kawaimiku`）登录
2. 进入聊天室后即可与其他在线用户实时聊天
3. 支持登出，登出后会广播用户下线状态

## 代码入口说明

- 登录逻辑：`app.py` 的 `login` 路由
- 消息处理与广播：`handle_message` 事件
- 在线用户管理：`handle_connect` 和 `handle_disconnect` 事件

如需自定义或扩展功能，请修改 `app.py` 文件
