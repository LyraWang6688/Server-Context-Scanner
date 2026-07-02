# Server Context Scanner

Server Context Scanner 是一个人为触发的服务器上下文采集器。

它的目标不是自动部署，也不是修改服务器，而是通过一个只读脚本生成一份 AI 可直接阅读的服务器状态报告。

默认报告是精简版，适合直接复制给 AI；需要排障时可以使用 `--full` 生成完整诊断报告。

## 适用场景

- 新增项目前，让 AI 了解服务器现状。
- 排查问题前，快速收集端口、运行环境、项目目录、Nginx、Docker、PM2 状态。
- 项目交接前，生成一份当前服务器上下文报告。
- 与 AI 对话时，减少重复手动执行运维命令。

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
├── reports/
│   ├── server_context_YYYYMMDD_HHMMSS.md
│   └── server_context_latest.md
└── README.md
```

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

## 报告内容

默认精简报告会包含：

- 服务器基础信息：用户、主机名、时间、系统、CPU、内存、磁盘。
- 运行环境：Node、npm、npx、Git、Python、PM2、Docker、systemd、Nginx。
- 端口占用：监听 TCP 端口和常见端口快速检查。
- 运行服务：PM2 应用、Docker 容器、Nginx 路由摘要。
- 疑似项目识别：项目路径、Git 状态、关键文件、运行方式线索。
- package.json 摘要：`name`、`version`、`scripts`、依赖数量、框架线索。
- 敏感文件：只列 `.env*` 文件名，不读取内容。
- Nginx 入口：`listen`、`server_name`、`proxy_pass`。
- 快速风险信号：磁盘、内存、端口冲突、Nginx 配置注意事项。
- AI 阅读说明：提醒 AI 严格基于报告证据分析。

完整诊断报告 `scan-server --full` 会额外包含：

- 每个项目的完整 `ls -la`。
- package.json 的完整 dependencies / devDependencies 名称。
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
