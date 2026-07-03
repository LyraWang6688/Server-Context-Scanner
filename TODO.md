# TODO

> 更新日期：2026-07-03

## 1. 增加 `projects.yml` 项目注册表

状态：已实现

目标：增加一份人工维护的项目注册表，让扫描报告不仅能展示自动发现的信息，还能说明每个项目的业务含义、域名、端口、运行方式和备注。

计划字段：

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

验收标准：

- 已增加示例 `projects.yml.example` 模板。
- 当 `projects.yml` 存在时，扫描器可以读取它。
- Summary 报告已增加 `Registered Projects` 区块。
- 缺少 `projects.yml` 时，扫描器仍能正常运行。
- README 已补充项目注册表的维护方式。

## 2. 修复 Web UI 与终端 Docker 权限差异

优先级：中

目标：让终端 `scan-server` 和 Web UI 生成报告时的 Docker 容器输出保持一致。

当前现象：

- 终端执行 `scan-server` 可以列出 Docker 容器。
- Web UI 生成报告时可能显示 Docker socket 权限不足。

可能原因：

- PM2 托管的 `server-context-scanner-web` 进程可能没有继承当前 SSH 会话的 Docker 用户组权限。

排查命令：

```bash
id
getent group docker
pm2 pid server-context-scanner-web
cat /proc/$(pm2 pid server-context-scanner-web)/status | grep -E "Uid|Gid|Groups"
```

可能修复方式：

- 使用更新后的环境重启 Web UI：

```bash
pm2 restart server-context-scanner-web --update-env
```

- 如果 PM2 daemon 的用户组权限仍是旧的，保存状态后谨慎重启 PM2：

```bash
pm2 save
pm2 kill
pm2 resurrect
pm2 status
```

验收标准：

- 当 `ubuntu` 用户具备 Docker 权限时，Web UI summary 报告也能列出 Docker 容器。
- 如果 Docker 权限不可用，报告继续保留当前清晰的权限说明。
- 不误删 PM2 应用，不让现有 PM2 服务异常离线。

## 3. 增加 `projects.yml` 注册表一致性检查

优先级：中

目标：新增一个人工触发的注册表检查能力，用于对比服务器当前扫描结果和 `projects.yml`，提醒用户新增、修改或下线项目登记信息。

建议命令：

```bash
scan-server --check-registry
```

检查范围：

- Nginx 路由：识别新增域名、端口变化、未登记的 `server_name -> proxy_pass`。
- PM2 应用：识别新增 PM2 进程、已登记但未运行的 PM2 项目。
- Docker 容器：识别新增容器、已登记但未运行的 Docker 项目。
- Git 项目目录：识别新增项目目录、Git remote 与 `projects.yml` 不一致。
- 端口：识别已登记端口和当前监听端口不一致。
- 状态：提示运行中的项目不应标记为 `inactive`，或长期未发现的项目可能需要标记为 `inactive`。

输出内容：

- 建议新增：扫描发现但 `projects.yml` 缺失的项目。
- 建议修改：域名、端口、运行方式、容器名、PM2 名称或 Git 仓库不一致。
- 可能废弃：`projects.yml` 中存在，但当前扫描未发现对应运行证据。
- 建议命令：告诉用户如何编辑、验证和重新生成报告。

后续 Web UI：

- 增加“检查项目注册表”按钮。
- 在前端显示检查报告和建议 `projects.yml` 片段。
- 第一版只给建议，不自动修改服务器文件。

后续 Skill：

- 稳定后再封装为 `server-project-registry-maintainer`。
- 触发场景：用户新增、更新、下线服务器项目，或需要对比 `scan-server` 报告和项目注册表。

验收标准：

- 没有 `projects.yml` 时能提示创建方式。
- 有 `projects.yml` 时能生成一致性检查报告。
- 检查报告包含建议新增、建议修改、可能废弃三类结果。
- Web UI 可以人工触发检查。
- 不自动修改 `projects.yml`，除非未来用户明确确认。

## 4. 排除 IDE / 远程开发工具内部目录

优先级：低

目标：避免把 TRAE、VS Code、Cursor 等远程开发工具自身目录误识别为业务项目。

需要排除的路径：

```bash
-not -path "*/.trae-cn-server/*"
-not -path "*/.vscode-server/*"
-not -path "*/.cursor-server/*"
```

原因：

- 这些目录可能包含 `package.json`，但不是用户业务项目。
- 当前自动发现可能把 `/home/ubuntu/.trae-cn-server/bin/stable-*` 识别为项目，污染报告。
- 不建议删除这些目录，因为它们可能是远程开发工具的服务端组件。

验收标准：

- `Detected Projects` 不再出现 `.trae-cn-server`、`.vscode-server`、`.cursor-server` 内部目录。
- 只改变扫描排除逻辑，不删除任何实际文件。

## 5. 增加服务器磁盘与缓存健康检查报告

优先级：中

目标：新增一个只读健康检查报告，帮助不熟悉 Linux 的用户判断是否需要清理旧日志、旧 Docker 镜像、旧报告或无用缓存。

建议命令：

```bash
scan-server --health
```

检查范围：

- 根磁盘使用率：例如超过 80% 标记 warning，超过 90% 标记 critical。
- 内存和 Swap：识别可用内存偏低或 Swap 使用偏高。
- Scanner 历史报告：统计 `reports/server_context_*.md` 数量和占用。
- PM2 日志：统计 `~/.pm2/logs` 占用。
- systemd journal：读取 `journalctl --disk-usage`。
- Docker 占用：读取 `docker system df`，权限不足时给清晰提示。
- npm / pnpm 缓存：统计 `~/.npm`、`~/.pnpm-store` 占用。
- apt 缓存：提示可执行 `sudo apt clean` 和 `sudo apt autoremove`。

输出内容：

- 当前占用摘要。
- 风险等级。
- 推荐清理顺序。
- 每一步的命令和风险说明。

建议的低风险清理命令：

```bash
pm2 flush
sudo journalctl --vacuum-time=7d
sudo apt autoremove -y
sudo apt clean
cd ~/server-context-scanner/reports
ls -1t server_context_*.md | tail -n +21 | xargs -r rm --
docker system prune
```

安全要求：

- 第一版只生成报告和建议，不自动执行清理。
- Docker 清理必须区分 `docker system prune` 和 `docker image prune -a` 的风险。
- 所有删除类命令必须让用户人工确认。

关于腾讯轻量应用服务器：

- 腾讯云控制台适合查看 CPU、内存、磁盘、带宽等大盘指标。
- 控制台通常不能精确判断是 PM2 日志、Docker 镜像、journal 还是项目缓存占空间。
- 具体清理仍建议通过服务器命令行排查后决定。
- Web UI 可以把这些命令行排查结果包装成更易读的报告，降低 Linux 使用门槛。

验收标准：

- Web UI 增加“生成健康检查报告”按钮。
- 报告只读，不自动清理。
- 报告能告诉用户“为什么磁盘高、建议先清理什么、对应命令是什么”。
