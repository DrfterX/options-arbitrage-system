# 期权期货交易系统 — 全面任务拆解 Plan

> 生成日期: 2026-06-10
> 扫描基础: 代码库全覆盖 + 186/186 测试通过 ✅

---

## 目标

将期权期货交易系统从"可运行的信号平台"推进到"具备实盘价值的生产系统"。聚焦于提升信号质量、补齐关键缺失功能、自动化运维。

---

## 系统现状

| 维度 | 状态 |
|------|------|
| 基础设施（DB/Schema/品种注册） | ✅ 完成 |
| 期货 N 型信号引擎 | ✅ 完成 |
| 期权策略引擎 | ✅ 完成（Black-76 / 比例价差 / 铁鹰式 / 宽跨式） |
| 信号中心 + 去重推送 | ✅ 完成 |
| Web 看板（Flask+ECharts） | ✅ 完成（localhost:5100）|
| SmartFilter 信号过滤 | ✅ 完成（回测 5096 条驱动）|
| 回测引擎 | ✅ 完成（6430 条历史信号）|
| 铁矿石 API（BluePrint） | ✅ 完成 |
| Telegram 推送 | ⬜ 未配置 Bot Token |
| 自动扫描 | ⬜ Plist 已加载但需验证 |
| 实盘交易接口 | ⬜ 未实现 |
| 持仓管理 | ⬜ 未实现 |
| 测试覆盖（期权侧） | ⬜ 2 个测试文件，覆盖不足 |
| CI/CD | ⬜ 未实现 |

---

## 任务分解

### P0 — 高优先级（提升系统价值）

#### 任务 1: Telegram Bot 推送配置 + dispatch 验证

> 预估: 10 分钟 | 依赖: 无 | 独立

- [ ] 注册 Telegram Bot（@BotFather）获取 token
- [ ] 获取 chat_id
- [ ] 写入 `config/settings.py` 的 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`
- [ ] 运行 `python -m pipeline.orchestrator --mode futures` 验证 dispatch Telegram 模式

**验收**: 扫描完成后能通过 Telegram 收到推送消息

---

#### 任务 2: 前端 SmartFilter 状态面板

> 预估: 15 分钟 | 依赖: 无 | 独立

- [ ] `web/templates/dashboard.html` 增加"过滤状态"区域
- [ ] 显示最近被过滤抑制的信号（品种、评分、原因）
- [ ] 显示 SmartFilter 统计：总过滤/推送/抑制数
- [ ] 新增 API `/api/filter-stats` 返回过滤统计数据

**验收**: dashboard 页面可见过滤面板，展示被抑制的信号及原因

---

#### 任务 3: 扩大验证信号样本量 — 自动化回测 + 仪表盘

> 预估: 20 分钟 | 依赖: 无 | 独立

- [ ] `futures/backtest.py` 添加每日自动回测入口（`run_daily_backtest(db)`）
- [ ] 回测结果持久化到 `system_config` 表
- [ ] dashboard 增加"回测健康度"区域：准确率趋势、品种准确率排序、L1/L2 穿透率
- [ ] 更新 SmartFilter `_SYMBOL_ACCURACY` 的自动化更新机制（目前是手写的）

**验收**: dashboard 可见回测统计面板，准确率数据每日自动更新

---

#### 任务 4: Web 服务 PM2 自启动

> 预估: 10 分钟 | 依赖: 无 | 独立

- [ ] 创建 `scripts/com.auto-company.web.plist` — launchd 启动 PM2
- [ ] 参考现有 `scripts/start_services.sh` 的 PM2 命令
- [ ] `launchctl load` 加载
- [ ] 验证开机后 Web 服务自动恢复

**验收**: 重启后 `http://localhost:5100` 可访问

---

### P1 — 中等优先级（补齐质量短板）

#### 任务 5: 期权引擎测试覆盖

> 预估: 20 分钟 | 依赖: 无 | 独立

- [ ] `tests/test_options/test_ratio_spread.py` — 比例价差计算
- [ ] `tests/test_options/test_multi_strategy.py` — 铁鹰式 + 宽跨式
- [ ] `tests/test_options/test_smart_filter.py` — SmartFilter 单元测试（已有部分）
- [ ] `tests/test_signals/test_dispatcher.py` — 推送去重测试
- [ ] `tests/test_signals/test_formatter.py` — 格式化测试

**验收**: 新增 ≥30 个测试，总测试 ≥200，全部通过

---

#### 任务 6: IV 历史回填 + 数据库维护

> 预估: 15 分钟 | 依赖: 无 | 独立

- [ ] 运行 `scripts/backfill_iv_history.py` 补全 IV 数据
- [ ] 添加 `system_config` 记录最后回填时间
- [ ] 添加定时回填逻辑（每周自动跑一次）
- [ ] 数据库 ANALYZE 优化查询性能

**验收**: IV 百分位数据覆盖到所有期权品种，query 性能合理化

---

#### 任务 7: 自动扫描脚本验证 + 异常告警

> 预估: 15 分钟 | 依赖: 无 | 独立

- [ ] 验证 `auto_scan.sh` 在 launchd 下工作正常（检查日志 `/Users/ayong/.hermes/logs/launchd.*.log`）
- [ ] 添加扫描失败告警（Telegram 推送）
- [ ] 添加扫描超时检测（1800s 后强制退出）
- [ ] 添加合约换月期数据空洞检测

**验收**: 自动扫描日志可回溯，失败时 Telegram 告警

---

### P2 — 低优先级（锦上添花 / 远期）

#### 任务 8: 实盘交易接口调研（CTP / 通达信 / 掘金）

> 预估: 20 分钟 | 依赖: 无 | 独立

- [ ] 调研可行接入方案（CTP 实盘直达 / 通达信 API / 掘金量化）
- [ ] 输出调研报告到 `docs/trading-interface-research.md`
- [ ] 评估各方案的成本、门槛、稳定性

**验收**: 产出调研文档，明确推荐方案

---

#### 任务 9: 持仓管理模块原型

> 预估: 20 分钟 | 依赖: 任务 8 | 独立

- [ ] 设计持仓表 schema（`positions` 表）
- [ ] `core/schema.py` 增加第 11 张表
- [ ] 实现 `PositionManager` 类：开仓/平仓/持仓查询
- [ ] 与 SignalHub 联动：推送信号后自动建立持仓记录

**验收**: `PositionManager` 可通过 SQL 查询持仓状态

---

#### 任务 10: CI/CD 配置（GitHub Actions）

> 预估: 15 分钟 | 依赖: 无 | 独立

- [ ] `.github/workflows/test.yml` — pytest 自动运行
- [ ] `.github/workflows/deploy.yml` — 部署 web 服务
- [ ] 测试运行结果 PR 自动检查

**验收**: PR 提交后自动跑测试并显示结果

---

## 依赖关系图

```
P0:
  任务 1 ── Telegram 推送（独立，最优收益）
  任务 2 ── 前端过滤面板（独立）
  任务 3 ── 自动化回测（独立）
  任务 4 ── Web 自启动（独立）

P1:
  任务 5 ── 测试覆盖（独立）
  任务 6 ── IV 回填（独立）
  任务 7 ── 扫描验证（独立）

P2:
  任务 8 ── 实盘调研（独立）
  任务 9 ── 持仓管理 ─(依赖任务 8)─→ 需先确定接口方案
  任务 10 ── CI/CD（独立）
```

**关键**: P0 任务之间完全独立，可并行或在任一顺序执行。每个任务 ≤20 分钟，可在一个 Cycle 内完成。

---

## 推荐执行顺序

1. **Cycle 1 (本轮)**: 产出 Plan ✅（完成）
2. **Cycle 2**: 任务 1 — Telegram Bot 配置推送（10min）
3. **Cycle 3**: 任务 2 — 前端过滤面板（15min）
4. **Cycle 4**: 任务 3 — 自动化回测仪表盘（20min）
5. **Cycle 5**: 任务 4 — Web 自启动（10min）
6. **Cycle 6**: 任务 5 — 测试覆盖（20min）
7. **Cycle 7**: 任务 7 — 扫描验证（15min）
8. **Cycle 8**: 任务 6 — IV 回填（15min）
9. **后续**: P2 任务按需执行
