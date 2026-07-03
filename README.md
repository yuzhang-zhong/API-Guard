# API Guard

API Guard 是一个用于安全管理 API Key、Token 和服务密钥的轻量工具。它通过系统级密钥库保存凭据，并在运行命令时将密钥注入到环境变量中，避免把敏感信息写入代码、`.env`、日志或 Git 仓库。

## 功能

- 安全存储 API 凭据
- 默认脱敏查看密钥
- 将密钥注入到子进程环境变量中
- 支持删除、列出和轮换凭据
- 避免明文 fallback，降低泄露风险

## 目录结构

API-Guard/
├── api-guardian/
│   ├── agents/
│   │   └── openai.yaml
│   ├── scripts/
│   │   └── api_guard.py
│   └── SKILL.md
└── .gitignore
环境要求
Python 3.10+
Windows：Windows Credential Manager
macOS：Keychain
Linux：Secret Service / secret-tool

Linux 上如果缺少 secret-tool，请先安装 libsecret-tools。

快速开始

进入工具目录：

cd api-guardian
保存密钥

推荐使用隐藏输入：

python scripts/api_guard.py store openai

也可以从环境变量导入：

python scripts/api_guard.py store openai --from-env OPENAI_API_KEY

或通过 stdin 导入：

printf "%s" "$OPENAI_API_KEY" | python scripts/api_guard.py store openai --stdin
查看密钥

默认只显示脱敏结果：

python scripts/api_guard.py get openai

确实需要明文时：

python scripts/api_guard.py get openai --reveal
在命令中使用密钥

将已保存的密钥注入为环境变量：

python scripts/api_guard.py run openai OPENAI_API_KEY -- python app.py

也可以运行其他命令：

python scripts/api_guard.py run openai OPENAI_API_KEY -- npm test
列出和删除凭据
python scripts/api_guard.py list
python scripts/api_guard.py delete openai
安全建议
不要把真实 API Key 写进 README、代码、.env 或日志
示例中统一使用 <API_KEY>、OPENAI_API_KEY 等占位符
提交前检查：
git status --short
git diff
git diff --cached
如果密钥已经泄露，应立即在服务商后台轮换，并删除仓库中的泄露记录
Agent 配置

agents/openai.yaml 提供了 OpenAI agent 的展示名称、简短描述和默认提示，可用于把 API Guard 作为凭据安全管理工具接入 agent 工作流。
