# API Guard

API Guard 是一个用于安全管理 API Key、Token 和服务密钥的轻量工具。它通过系统级密钥库保存凭据，并在运行命令时将密钥注入到环境变量中，避免把敏感信息写入代码、`.env`、日志或 Git 仓库。

## 功能

- 安全存储 API 凭据
- 默认脱敏查看密钥
- 将密钥注入到子进程环境变量中
- 支持删除、列出和轮换凭据
- 避免明文 fallback，降低泄露风险

## 目录结构

```text
API-Guard/
├── api-guardian/
│   ├── agents/
│   │   └── openai.yaml
│   ├── scripts/
│   │   └── api_guard.py
│   └── SKILL.md
└── .gitignore
