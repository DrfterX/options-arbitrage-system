# Plan: 修复 SQLite 并发冲突

## 目标
解决 `data_refresh()` 中 595+ 并行数据库操作导致的 `unable to open database file` 错误

## 根因
`Database.get_conn()` 每次调用创建新连接，61MB SQLite WAL 在密集并发下竞争锁

## 修复方案

### 方案 A：单例连接池（推荐）
- `Database` 实例持有单一共享连接
- 所有子函数复用该连接
- 增加 `timeout=30` 和 `PRAGMA busy_timeout=5000`

### 方案 B：最小改动的修补
- 只在 `Database.get_conn()` 增加 `timeout=30` 和 `PRAGMA busy_timeout=5000`

### 选择
选方案 B（最小改动），验证效果后再决定是否升级到方案 A

## 拆解步骤

### 步骤 1：修复 Database.get_conn()
- 增加 timeout 参数
- 增加 busy_timeout pragma

### 步骤 2：验证修复效果
- 运行 `python -m pipeline.orchestrator --mode all`
- 检查日志中 N 型检测总数（应 > 0）

## 预计工作量
1 Cycle
