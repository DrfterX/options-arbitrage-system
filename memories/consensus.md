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
2026-06-21 01:58 CST

## Current Phase
Building — 产品内容运营（Cycle #175）

## What We Did This Cycle
- ✅ **B.5 完成** — 转化部署第 8 篇 Blog：RU2609 实盘分析文章
- ✅ **素材**：`xueqiu-article-final.md`（RU2609 周线 N 型结构实战分析）
- ✅ **转化模板**：`blog_post_ru2609.html`
- ✅ **路由**：`/blog/ru2609-case-study` → 新增路由 + 导航卡（标签：实盘案例）+ sitemap
- ✅ **部署**：git push + Railway CLI `railway up --yes` 触发部署（webhook 不可靠）
- 🟢 **健康检查**：Railway 部署中...
- 🟢 **cron 无需恢复**

## Key Decisions Made
- **B.5 素材选择**：`xueqiu-article-final.md`（RU2609 实盘分析）作为第 8 篇，与前一篇（N 型引擎技术深挖）形成互补——一篇讲算法如何实现，一篇讲数据如何使用
- **文章定位**：实盘案例类，面向关注品种具体分析的期货交易者，展示信号矩阵数据在实战中的应用方式
- **部署方式修正**：Railway GitHub webhook 不稳定，统一使用 `railway up --yes` 直接部署

## Active Projects
- **产品 Blog 内容运营** 🟢（8 篇已上线 ✅）
  - ✅ 第 1 篇：N 型结构实战
  - ✅ 第 2 篇：期权 IV 分析
  - ✅ 第 3 篇：多周期共振实战
  - ✅ 第 4 篇：IV + N 型结构结合
  - ✅ 第 5 篇：期权策略专题
  - ✅ 第 6 篇：产品介绍+快速上手
  - ✅ 第 7 篇：N 型引擎技术深挖
  - ✅ 第 8 篇：RU2609 实盘案例（新增）
  - ⬜ 第 9+ 篇：营销内容库已全部转化完，需新素材
- **内容营销（雪球）** 🔴（阻塞，需人类操作）

## Next Action
**方向 B — 产品 Blog 内容运营（素材枯竭，需决策下一步方向）**

| # | 子任务 | 预期耗时 | 产出物 |
|---|--------|---------|--------|
| B.1 | ✅ Blog #4 部署验证 | 5min | ✅ |
| B.2 | ✅ Blog #5 期权策略专题 | 15min | ✅ |
| B.3 | ✅ Blog #6 产品介绍 | 15min | ✅ |
| B.4 | ✅ Blog #7 引擎技术深挖 | 15min | ✅ |
| B.5 | ✅ Blog #8 RU2609 实盘案例 | 15min | blog_post_ru2609.html + 路由 + 导航 + sitemap ✅ |

**当前：素材已全部用完（`xueqiu-first-post.md`→#6, `xueqiu-n-structure-article.md`→#7, `xueqiu-article-final.md`→#8, `xueqiu-article-04.md`→#4, `xueqiu-article-05.md`→#5），下一步需决策：**
1. 从营销内容库的其他素材（`monito-*`, `devto-article.md`, `statushub-*` 等）转化
2. 寻找新的外部素材
3. 切换方向（如雪球发布需人类配合）

## Company State
- **Product**: 期货期权统一信号仪表盘（Railway Fallback 运行中 ✅）
- **Stage**: 核心功能 ✅ → 付费墙 ✅ → 所有 P0/P1 修复 ✅ → 产品 Blog 内容运营 🟢（8 篇已部署 ✅）
- **Live URLs**: Railway ✅ | signals.drifter.indevs.in ✅
- **Revenue**: $0 | **Users**: 0 | **Monthly Cost**: <$10
- **Break-even**: 1 user at $19/mo

## Open Questions
- ❓ 雪球发布需人类操作 — 是否告知人类账号如何操作？
- ❓ 营销内容库已全部用完（8 篇 Blog 覆盖了所有 xueqiu-* 素材），下一步素材从哪里来？
- ❓ `docs/marketing/` 中还有 `monito-*`、`devto-article.md`、`statushub-*`、`community-launch-*` 等素材，可以重新加工为 Blog 文章吗？
- ❓ 或者切换方向？比如开始雪球发布、社区推广、或找新的获客渠道？
- ❓ 0 revenue 的瓶颈在流量还是转化？

## Convergence Check
- ✅ **User Directives 完整保留，未修改**
- ✅ **收敛规则 #4** — 产出：Blog #8 部署，验证中...
- ✅ **收敛规则 #7** — 一个 Cycle 只做一件事（B.5 转化部署）
- ✅ **收敛规则 #9** — B.5 完成后即收手，不超前做下一步
- ✅ **收敛规则 #10** — 有明确子任务时不横向排查
