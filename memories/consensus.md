# Auto Company Consensus

## User Directives（由人类维护，自动循环必须完整保留，严禁修改或删除）

### 🧠 项目自主性推理优化原则（通用指导）

人类发现了 A 问题，不代表只有 A 问题。系统应具备自主推理能力：

0. **（有明确任务时不发散）** 如果共识的 Next Action 有明确可执行的子任务，**跳过此原则直接执行**，不要横向排查、向上追溯或推理关联影响。此原则仅在 Next Action 为空或方向不明时使用。
1. **同类缺陷横向排查** — 人类发现某个模块有 bug 时，自动推理同类模块是否存在同样问题。例如：期货 K 线发现 N 型结构算法缺陷 → 自动检查期权面板是否用了同类型结构算法 → 如有则一并排查
2. **问题根源向上追溯** — 发现一个表面问题时，向上追溯一层：这是独立的 bug， 还是某个底层机制/框架/工具的共性缺陷？如果是共性缺陷，一次性修复比逐个修更有效
3. **关联影响链推理** — 修 A 时可能影响 B。自动推理修复影响范围，避免修好一个炸了另一个
4. **模式识别 & 预防** — 人类指出一类问题后（如 K 线显示不准），系统应主动搜索是否还有其他品种/周期/面板存在类似偏差，不要等人类逐个指出
5. **输出形式** — 推理结果写入共识的「Open Questions」或下一轮 Next Action 中，供人类 review，不擅自发起大规模重构

### ⚡ Railway 备份机制（2026-06-20 上线）

- **本机主用**（127.0.0.1:5100）— 正常情况本机服务
- **Railway 备用**（optionsarbitragesystem-production.up.railway.app）— 停电/本机关闭时自动接管
- **同步方式**：GitHub push → Railway 自动部署（GitHub webhook），无需手动干预
- **同步脚本**：`scripts/core/railway-sync.sh`（提交+推送+触发部署+健康检查）
- **状态监控**：`scripts/core/backup-check.sh` → 输出 `logs/backup-status.json`
- **域名**：Railway 自带域名 `optionsarbitragesystem-production.up.railway.app`

---

## Last Updated
2026-06-29 00:10 CST

## Current Phase
审计报告修复（全部 15 项核心修复完成）

## What We Did This Cycle
- ✅ **P1 期权面板 UI/UX 修复全部完成**
- ✅ **审计 F1** — Iron Condor `max_loss` 不对称翼修复：分别计算 Call/Put 两侧亏损显式取大
- ✅ **审计 F2** — `calc_iv` Newton 法加 Bisection 兜底：新增 `_newton_iv` + `_bisection_iv` 双阶段搜索
- ✅ **审计 F3** — `black_price` T≤0 返回到期内在价值（不再抛异常）
- ✅ **审计 F5** — Ratio Spread 添加 `max_loss_unbounded=True` 标志，传递到风控和前端
- ✅ **审计 F6** — `risk_manager.py` 盈亏比计算支持 `net_cost < 0`（权利金收入策略）+ 无界亏损警告
- ✅ **审计 Q1/E1** — `signals/hub.py` 改造：
  - 所有 DB 方法改为 `with self.db.get_conn() as conn:` 上下文管理器
  - 异常分类 `sqlite3.IntegrityError` → -2，其他 → -1
  - 失败时 `conn.rollback()` 避免部分写入
  - JSON 序列化失败捕获（E2）
- ✅ **审计 S1** — `options_signals` 表加字段：`days_to_expiry`/`margin_required`/`win_rate`/`breakeven_low`/`breakeven_high`
  - schema DDL + db.py 增量迁移 + hub.py INSERT + orchestrator signal dict 全链路贯通
- ✅ **审计 F4** — Ratio spread 胜率改为调用 `pricing.calc_win_rate`（统一 d_low 业务逻辑），移除不再使用的 `math`/`normal_cdf` import
- ✅ **审计 Q2** — `hub.py` L1/L2/L3 pass 重复表达式抽为 `_safe_int_pass()` helper
- ✅ **审计 Q3/S3** — SmartFilter 品种准确率去重（去除 `"Y"` 重复 key），加 `signal_kind='options'` 参数 + `_evaluate_option_signal` 方法，期权信号跳过期货准确率检查
- ✅ **审计 Q5** — `formatter.py` 风控 emoji/中文 dict 从类内移到模块级（模块级定义 + 类引用兼容）
- ✅ **审计 S2** — 推送消息添加 DTE 和保证金字段
- ✅ **审计 S4** — 期权去重窗口从 12h 改为 1h（期货保持 12h）
- ✅ **审计 E3** — `dispatcher.py` Telegram 未配置时改为 `logger.error` + 每 30 分钟限频告警，加 `logger` 定义修复隐式 bug
- ✅ **审计 E4** — `add_warning` 不再立即置 `passed=False`，尾部 `evaluate_signal` 统一决定

## Next Action
**所有审计修复已完成 — 等待人类决定下一步方向**

可能的下一步方向：
1. **P2 功能开发**：新策略类型（日历价差、跨品种套利）、回测模块、风险分析面板
2. **获客/流量**：SEO 优化、内容营销、社交媒体推广
3. **Snowball 发布**：需人类操作账号完成发布
4. **技术优化**：IV percentile 实盘数据接入、ratio spread 统一评分函数、前端自适应权重

## Company State
- **Product**: 期货期权统一信号仪表盘（本地 + Cloudflare Tunnel）
- **Stage**: 核心功能 ✅ → 付费墙 ✅ → 所有 P0/P1 修复 ✅ → 产品 Blog 内容运营 ✅（8 篇已部署）→ **P1 期权面板 UI/UX 修复 ✅（全部完成）**
- **Live URLs**: signals.drifter.indevs.in ✅
- **Revenue**: $0 | **Users**: 0 | **Monthly Cost**: <$10
- **Break-even**: 1 user at $19/mo

## Open Questions
- ❓ 下一步主方向：P2 功能开发 vs 获客/流量 vs Snowball 发布 vs 技术优化？

## Convergence Check
- ✅ **User Directives 完整保留，未修改**
- ✅ **收敛规则 #4** — 产出：options_dashboard.html SSR 排序修复，已提交推送
- ✅ **收敛规则 #7** — 一个 Cycle 只做一件事（P1.2.2 SSR 排序修复）
- ✅ **收敛规则 #9** — P1.2.2 完成后即收手，不超前做下一步
- ✅ **收敛规则 #10** — 明确转向 P1 方向后，跳过发散推理直接执行子任务