# Server Context Scanner

Server Context Scanner 是一个人为触发的服务器上下文采集器。

它的目标不是自动部署，也不是修改服务器，而是通过一个只读脚本生成一份 AI 可直接阅读的服务器状态报告。

默认报告是精简版，适合直接复制给 AI；需要排障时可以使用 `--full` 生成完整诊断报告。

## 适用场景

- 新增项目前，让 AI 了解服务器现状。
- 排查问题前，快速收集端口、运行环境、项目目录、Nginx、Docker、PM2 状态。
- 项目交接前，生成一份当前服务器上下文报告。
- 与 AI 对话时，减少重复手动执行运维命令。

## 项目边界

当前版本主要面向单台 Ubuntu/Linux 服务器。

正式支持：

- Ubuntu Server 20.04 / 22.04 / 24.04。
- Debian 系 Linux 服务器。
- 使用 Bash、systemd、Nginx、Docker、PM2、Node、Python 的常见 Web 应用服务器。
- 通过 SSH 执行 `scan-server`，或在服务器本机运行 Flask Web UI 后通过 Nginx 反向代理访问。

暂未正式支持：

- Windows Server。
- macOS 服务器或 macOS 本机开发环境扫描。
- Kubernetes 集群级别扫描。
- 多服务器集中监控。
- 云厂商资源扫描，例如安全组、负载均衡、RDS、对象存储。

不是本项目目标：

- 自动部署平台。
- 企业级监控系统。
- 安全审计工具。
- 云资源管理工具。
- 自动修复、自动停止服务或自动重启服务。

如果未来需要支持 Windows 或 macOS，建议新增独立采集器，例如 `scan_windows_context.ps1` 或 `scan_macos_context.sh`，不要把当前 Linux Bash 脚本硬改成跨平台脚本。

## 安全边界

脚本遵守以下原则：

- 只读扫描。
- 不删除文件。
- 不停止服务。
- 不重启服务。
- 不修改 Nginx 配置。
- 不修改 Docker / PM2 / systemd。
- 不读取 `.env` 内容，只列出 `.env*` 文件名。
- 不输出环境变量值，只输出环境变量名。

## 目录结构

```text
server-context-scanner/
├── scan_server_context.sh
├── install.sh
├── ai_prompt_template.md
├── projects.yml.example
├── reports/
│   ├── server_context_YYYYMMDD_HHMMSS.md
│   └── server_context_latest.md
└── README.md
```

## 运行环境

- Bash：执行只读扫描脚本。
- Python 3：解析 PM2 JSON 和 `package.json` 摘要；Ubuntu 22.04 默认已内置。
- 可选工具：Git、Node、npm、PM2、Docker、Nginx、systemd。脚本会按实际安装情况探测，未安装时只在报告中标记为 `not-found` 或对应提示。

## 安装

把整个 `server-context-scanner` 目录复制到服务器后，执行：

```bash
cd ~/server-context-scanner
chmod +x install.sh
./install.sh
source ~/.bashrc
```

`install.sh` 会更新 `~/.bashrc` 中由以下标记包裹的快捷命令区块：

```bash
# Begin Server Context Scanner
# End Server Context Scanner
```

安装脚本只会管理这个标记区块和旧版 `scan-server` alias，不会主动修改其他 shell 配置。重新运行 `install.sh` 会刷新这个快捷命令。

每次运行 `install.sh` 前都会自动备份当前 `~/.bashrc`：

```text
~/.bashrc.server-context-scanner.bak.YYYYMMDDHHMMSS
```

如果需要恢复，可以执行：

```bash
cp ~/.bashrc.server-context-scanner.bak.YYYYMMDDHHMMSS ~/.bashrc
source ~/.bashrc
```

如果你不想修改 `~/.bashrc`，可以不运行 `install.sh`，只执行：

```bash
chmod +x ~/server-context-scanner/scan_server_context.sh
```

## 使用

推荐方式，生成精简版 AI 上下文报告：

```bash
scan-server
```

它会自动：

```text
1. 执行只读服务器扫描
2. 生成 reports/server_context_YYYYMMDD_HHMMSS.md
3. 更新 reports/server_context_latest.md
4. 把最新报告打印到终端，方便复制给 AI
```

需要完整诊断报告时：

```bash
scan-server --full
```

查看帮助：

```bash
scan-server --help
```

不使用快捷命令时：

```bash
~/server-context-scanner/scan_server_context.sh
cat ~/server-context-scanner/reports/server_context_latest.md
```

不使用快捷命令时，也可以直接给脚本传参：

```bash
~/server-context-scanner/scan_server_context.sh --full
cat ~/server-context-scanner/reports/server_context_latest.md
```

## 项目注册表

`projects.yml` 是一份人工维护的项目注册表，用来补充自动扫描无法判断的业务信息，例如项目名、域名、端口、运行方式和备注。

仓库提供模板文件：

```bash
cp projects.yml.example projects.yml
nano projects.yml
```

真实的 `projects.yml` 已被 `.gitignore` 忽略，默认不会提交到 GitHub，适合保存服务器本地的业务备注。

示例：

```yaml
projects:
  - name: ReadInsight
    path: /opt/readinsight
    domain: readinsight.bamamei.online
    port: 3000
    runtime: docker
    container: readinsight-web
    repo: https://github.com/winnie6688/ReadInsight.git
    status: production
    notes: 阅读分析 Web 应用，Nginx 反代到 127.0.0.1:3000。
```

支持字段：

- `name`：项目名称。
- `path`：服务器上的项目目录。
- `domain`：公网域名，如有。
- `port`：宿主机端口或内部服务端口。
- `runtime`：`pm2`、`docker`、`docker-compose`、`systemd` 或 `manual`。
- `pm2_name`：PM2 应用名，如适用。
- `container`：Docker 容器名，如适用。
- `repo`：Git 仓库地址。
- `status`：`production`、`staging`、`inactive` 或 `unknown`。
- `notes`：简短业务说明或运维备注。

当 `projects.yml` 存在时，默认 summary 报告会增加 `Registered Projects` 区块；如果不存在，扫描器仍会正常运行。

## Web UI

如果你希望跨设备使用，可以启动 Web UI。Web UI 提供按钮触发扫描、一键复制报告、下载 Markdown 和清空页面。

安装依赖：

```bash
cd ~/server-context-scanner
python3 -m pip install -r requirements.txt
```

本机启动：

```bash
SERVER_CONTEXT_WEB_HOST=127.0.0.1 SERVER_CONTEXT_WEB_PORT=8765 python3 web_app.py
```

打开：

```text
http://127.0.0.1:8765
```

如需增加应用层 Token：

```bash
SERVER_CONTEXT_WEB_TOKEN='替换成强随机字符串' python3 web_app.py
```

启用 Token 后，前端会通过 `X-Scanner-Token` 请求头调用 API 和下载报告，避免把 Token 放在 URL query 中。

### PM2 启动示例

```bash
cd ~/server-context-scanner
SERVER_CONTEXT_WEB_HOST=127.0.0.1 SERVER_CONTEXT_WEB_PORT=8765 \
pm2 start web_app.py --name server-context-scanner-web --interpreter python3
```

### 跨设备访问建议

跨设备访问时，不建议直接暴露 Flask 服务。推荐：

```text
浏览器
  ↓ HTTPS
Nginx + Basic Auth
  ↓
127.0.0.1:8765 Flask Web UI
```

Nginx 反向代理示例：

```nginx
server {
    listen 80;
    server_name scanner.example.com;

    auth_basic "Server Context Scanner";
    auth_basic_user_file /etc/nginx/.htpasswd-server-context-scanner;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

上线前建议：

- 使用 HTTPS。
- 启用 Basic Auth 或 `SERVER_CONTEXT_WEB_TOKEN`。
- 不要开放任意命令输入。
- Flask 服务只监听 `127.0.0.1`。
- 如果手动设置 `SERVER_CONTEXT_WEB_HOST=0.0.0.0` 且未设置 Token，服务启动时会打印安全警告；不建议直接公网暴露 Flask。

## 报告内容

默认精简报告会包含：

- 服务器基础信息：用户、主机名、时间、系统、CPU、内存、磁盘。
- 运行环境：Node、npm、npx、Git、Python、PM2、Docker、systemd、Nginx。
- 端口占用：常见端口快速检查。
- 运行服务：PM2 应用、Docker 容器、Nginx 路由摘要。
- 项目注册表：读取 `projects.yml`，输出人工维护的项目业务信息。
- 疑似项目识别：项目路径、Git 状态、关键文件、运行方式线索。
- package.json 摘要：`name`、`version`、关键 `scripts`、隐藏脚本数量、依赖数量、框架线索。
- 敏感文件：只列 `.env*` 文件名，不读取内容。
- Nginx 入口：逐文件解析并跟随 `sites-enabled` 符号链接，忽略注释行，精简为 `server_name -> proxy_pass`。
- 快速风险信号：磁盘、内存、端口冲突、Nginx 配置注意事项。
- AI 阅读说明：提醒 AI 严格基于报告证据分析。
- 为减少 AI 上下文占用，默认精简报告只展示命令标题和输出，不展示完整执行命令。

完整诊断报告 `scan-server --full` 会额外包含：

- 完整执行命令，便于审计和排障复现。
- 每个项目的完整 `ls -la`。
- package.json 的完整 scripts、dependencies / devDependencies 名称。
- 完整 `ss -lntp` 监听端口表。
- Git 最近 5 条提交。
- 详细 `systemctl status nginx --no-pager`。
- Node / PM2 / Docker 相关进程详情。
- 环境变量名列表，不输出变量值。

## 推荐工作流

```text
1. SSH 登录服务器
2. 执行 scan-server
3. 复制终端输出的 Markdown 报告
4. 把报告贴给正在对话的 AI
5. 让 AI 基于报告判断部署方案或排查方向
6. 人工确认后，再执行任何修改类命令
```

遇到复杂排障时，再执行：

```bash
scan-server --full
```

## 与 AI 对话

生成报告后，可以打开 `ai_prompt_template.md`，把里面的提示词和 `server_context_latest.md` 的内容一起发给 AI。

核心要求是：

- 严格基于报告内容分析。
- 报告中没有证据的事情要明确说明。
- 不建议删除文件。
- 不建议停止已有服务。
- 修改配置前必须先备份。
- 所有修改类操作必须先经过人工确认。

## 后续升级方向

- V2：增加 `projects.yml` 项目注册表，记录业务含义、负责人、域名、运行方式。
- V3：增加 `check_new_project.sh`，检查目标端口、项目目录、PM2 名称、Docker 容器名是否冲突。
- V4：基于扫描报告生成部署建议报告。
- V5：人工确认后执行半自动部署，并在部署后再次扫描验证。
