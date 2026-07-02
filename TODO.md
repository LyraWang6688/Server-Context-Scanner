# TODO

> 更新日期：2026-07-03

## 1. 增加 `projects.yml` 项目注册表

优先级：中

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

- 增加一个示例 `projects.yml` 模板。
- 当 `projects.yml` 存在时，扫描器可以读取它。
- Summary 报告增加 `Registered Projects` 区块。
- 缺少 `projects.yml` 时，扫描器仍能正常运行。
- README 补充项目注册表的维护方式。

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
