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
2026-06-21 02:10 CST

## Current Phase
Building — P1 期权面板 UI/UX 修复（Cycle #176）

## What We Did This Cycle
- ✅ **全量调查**：确认 P0 线 C（N 型结构动态刷新）已全部完成（算法修复 0 失败 + 3 条动态刷新路径 + 增量心跳线程 + API 去重算）
- ✅ **确认**：P0 B.3（Skeleton loading）已基本实现（动态行数、sector 分隔、级联动画俱全）
- ✅ **转向 P1**：Blog 内容管线素材已耗尽，转入 P1 期权面板 UI/UX 修复
- ✅ **P1.2.2 完成** — SSR 按评分排序：options 策略表和信号卡片的初始渲染改为按 `unified_score` 降序排列
  - 3 处 `options[:20]` → `(options|sort(attribute='unified_score', reverse=True))[:20]`
  - 包括 `_signalsData` JSON 数据源
  - 提交 & 推送至 GitHub → Railway 自动部署
- 🟢 **健康检查**：Railway ✅ 200 | signals ✅ 200 | 本机关闭

## Key Decisions Made
- **Blog 内容管线关闭**：xueqiu-* 素材已全部用完，docs/marketing/ 剩余素材均为其他产品（monito/StatusHub/Critiq），不适合直接转化
- **转向 P1 期权面板**：P0 线 C ✅ + P0 B.3 ✅，P1 成为下一个有实际工作的高优先级方向

## Active Projects
- **P1 期权面板 UI/UX 修复** 🟡（刚刚启动）
  - ✅ P1.2.2 SSR 按评分排序
  - ⬜ P1.1.1 IV 柱状图 xAxis label 拥挤
  - ⬜ P1.1.2 合约为 `n` 前缀清洗
  - ⬜ P1.1.3 中文名标注优化
  - ⬜ P1.2.1 详情图标点击不一致
  - ⬜ P1.2.3 评分算法透明度确认

## Next Action
**Step P1 — 期权面板 UI/UX 修复**

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| P1.2.2 | ✅ SSR 按评分排序 | 5min | ✅ 已完成 |
| **P1.1.1** | **IV 柱状图 xAxis label 拥挤修复** | **10min** | options_dashboard.html ECharts option |
| P1.1.2 | 合约为 n 前缀清洗 | 10min | app.py 添加清洗 |
| P1.1.3 | 中文名标注优化 | 10min | xAxis formatter |
| P1.2.1 | 详情图标点击不一致 | 20min | 排查 + 修复 |
| P1.2.3 | 评分算法透明度确认 | 5min | 验证记录 |

**当前：Step P1.1.1 — IV 柱状图底部 xAxis label 拥挤**
- 增加 `grid.bottom` 从 110 → 140
- xAxis label `fontSize` 从 9 → 8
- xAxis label 仅显示符号（简短），中文名移到 tooltip

## Company State
- **Product**: 期货期权统一信号仪表盘（Railway Fallback 运行中 ✅）
- **Stage**: 核心功能 ✅ → 付费墙 ✅ → 所有 P0/P1 修复 ✅ → 产品 Blog 内容运营 🟢（8 篇已部署 ✅）→ P1 期权面板 UI/UX 修复 🟡（启动）
- **Live URLs**: Railway ✅ | signals.drifter.indevs.in ✅
- **Revenue**: $0 | **Users**: 0 | **Monthly Cost**: <$10
- **Break-even**: 1 user at $19/mo

## Open Questions
- ❓ P1.1.1 xAxis 修复：仅符号展示是否足够？需保留中文名在 tooltip 中
- ❓ Snowball 发布需人类操作 — 是否告知人类账号如何操作？
- ❓ 0 revenue 的瓶颈在流量还是转化？
- ❓ P0 线 C + B 线全部完成确认后，后续主方向是继续 P1 还是转换到获客/流量方向？

## Convergence Check
- ✅ **User Directives 完整保留，未修改**
- ✅ **收敛规则 #4** — 产出：options_dashboard.html SSR 排序修复，已提交推送
- ✅ **收敛规则 #7** — 一个 Cycle 只做一件事（P1.2.2 SSR 排序修复）
- ✅ **收敛规则 #9** — P1.2.2 完成后即收手，不超前做下一步
- ✅ **收敛规则 #10** — 明确转向 P1 方向后，跳过发散推理直接执行子任务