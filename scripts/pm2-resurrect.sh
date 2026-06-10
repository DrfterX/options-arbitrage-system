#!/bin/bash
# PM2 进程恢复 — 开机自启动
# 恢复所有 PM2 管理的进程（options-trading web 服务等）
export PATH="/Users/ayong/.workbuddy/binaries/node/versions/22.22.2/bin:$PATH"
exec /Users/ayong/.workbuddy/binaries/node/versions/22.22.2/bin/pm2 resurrect
