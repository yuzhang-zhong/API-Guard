# API Guard

API Guard 是一个轻量级 API 凭据管理工具，用于安全保存、读取和使用 API Key、Token 与服务密钥。

它会优先把凭据保存到操作系统自带的密钥库中，并在运行命令时把密钥注入为环境变量，避免把敏感信息写进代码、`.env`、日志或 Git 仓库。

## Features

- 安全保存 API Key / Token / Service Secret
- 默认脱敏查看凭据
- 将凭据注入到子进程环境变量中
- 支持列出、删除和替换凭据
- 不提供明文文件 fallback，降低泄露风险

## Project Structure

```text
API-Guard/
├── api-guardian/
│   ├── agents/
│   │   └── openai.yaml
│   ├── scripts/
│   │   └── api_guard.py
│   └── SKILL.md
└── .gitignore
```

## Requirements

- Python 3.10+
- Windows：Windows Credential Manager
- macOS：Keychain
- Linux：Secret Service / `secret-tool`

Linux 用户如果缺少 `secret-tool`，可以安装：

```bash
sudo apt install libsecret-tools
```

## Usage

进入工具目录：

```bash
cd api-guardian
```

### Store a credential

推荐使用隐藏输入保存密钥：

```bash
python scripts/api_guard.py store openai
```

从已有环境变量导入：

```bash
python scripts/api_guard.py store openai --from-env OPENAI_API_KEY
```

从 stdin 导入：

```bash
printf "%s" "$OPENAI_API_KEY" | python scripts/api_guard.py store openai --stdin
```

也可以直接传值，但不推荐，因为命令行参数可能出现在 shell history 或进程列表中：

```bash
python scripts/api_guard.py store openai --value "<API_KEY>"
```

### Get a credential

默认只显示脱敏结果：

```bash
python scripts/api_guard.py get openai
```

确实需要明文时：

```bash
python scripts/api_guard.py get openai --reveal
```

请不要把 reveal 出来的真实密钥粘贴到聊天、日志或代码中。

### Run a command with a credential

将保存的凭据注入为环境变量：

```bash
python scripts/api_guard.py run openai OPENAI_API_KEY -- python app.py
```

也可以运行其他命令：

```bash
python scripts/api_guard.py run openai OPENAI_API_KEY -- npm test
```

### List credentials

```bash
python scripts/api_guard.py list
```

部分平台可能不支持完整枚举。

### Delete a credential

```bash
python scripts/api_guard.py delete openai
```

### Rotate a credential

API Guard 没有单独的 `rotate` 命令。轮换凭据时，可以直接用新的密钥覆盖同名凭据：

```bash
python scripts/api_guard.py store openai
```

建议流程：

1. 在服务商后台生成新的 API Key
2. 使用 API Guard 保存新密钥
3. 用 `run` 做一次测试
4. 在服务商后台撤销旧密钥

## Naming

凭据名称建议使用简短的逻辑名称，例如：

```text
openai
github
stripe-prod
stripe-test
anthropic-dev
```

不要把真实密钥或敏感信息放进名称里。

## Git Safety

本仓库的 `.gitignore` 已忽略常见敏感文件，例如：

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
*secret*
*token*
*.sqlite
*.db
```

提交前建议检查：

```bash
git status --short
git diff
git diff --cached
git ls-files --others --exclude-standard
```

如果发现密钥已经被提交或泄露，请立即在服务商后台轮换密钥，并从仓库和 Git 历史中移除泄露内容。

## Agent Integration

`api-guardian/agents/openai.yaml` 提供了一个 OpenAI agent 配置，用于把 API Guard 作为安全凭据管理工具接入 agent 工作流。

默认说明为：

```text
Securely store and use API credentials
```

## Security Notes

- 不要在代码、README、日志或截图中出现真实 API Key
- 示例中使用 `<API_KEY>` 或环境变量名作为占位符
- 优先使用隐藏输入、stdin 或环境变量导入密钥
- 避免使用命令行参数直接传递真实密钥
- 如果密钥泄露，应视为已失效并立即轮换
