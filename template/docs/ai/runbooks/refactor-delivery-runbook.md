# 重构交付运行手册（refactor-specific）

> **本文档只描述"重构（refactor）"工作流相对通用 L2 三 Session 纪律的差异**。通用 L2 三 Session 纪律见 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)。

## 范围

本文档适用于 L2+ 重构任务。L0 / L1 重构可单 session 串完（用 [refactor-brief.md](../templates/refactor-brief.md) 记录行为不变量）。

> **已取代**：本 runbook 早前版本的"L2+ 强制 4 session"措辞已被 [ADR-0003](../../adr/0003-multi-session-l2.md) 2026-08-01 修订取代。**L2 现行规则是"规划 / 实施 / 评审"三 Session；spec 与 plan 始终是两份独立文件。**

## L2+ refactor 与 feature 的关键差异

- **规划 session 必含"行为不变量"**：refactor 的核心是"行为不变"，必须明确"什么不能变"（[refactor-brief.md](../templates/refactor-brief.md) 模板已要求）
- **规划 session 重点不同**：feature 关注"切片与可验证性"，refactor 关注"主战场文件 + 不应被改动的文件"
- **实施 session 重点不同**：feature 关注"新行为是否成立"，refactor 关注"每一步都跑相同测试 + 与 baseline 对比"
- **评审 session 重点不同**：feature 关注"边界 / 新功能完整性"，refactor 关注"行为不变量是否真被守住 / 是否有'顺手扩大'"

### verify 落点（与通用 L2 三 Session 纪律一致）

refactor 任务也遵守 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md) 的"verify 落点细则"：

- 实施 session 必须跑项目根目录 `verify`，**同时**写入 `docs/specs/<date>-<name>.md` **与** `docs/plans/<date>-<name>.md` 双份末尾的 `## 验证证据` 段
- 规划 session **不**跑 verify、**不**写 `## 验证证据` 段，仅接力 spec + plan 双份
- **不接受**"只写 spec 或只写 plan"——双份均必填
- 行为不变量通过 refactor 的双份 `## 验证证据` 段中"对比 baseline"行验证

### L3 refactor（Pre-Implementation Approval Gate）

L3 refactor 任务额外遵守 [ADR-0005](../../adr/0005-l3-approval-gate.md)：

- 实施 session 启动前必须收用户"已批准"信号并引用 spec / plan 双份路径
- `## 批准` 段（含第 8 项最小必含）必须位于 spec 与 plan 双份的 `## 验证证据` 段**之前**
- 批准**不得**跨任务复用——每个 refactor 任务独立走"spec + plan + 批准"全流程

## 规划 session 内的推荐切片顺序

规划 session 写 plan 时，建议按以下顺序拆分任务切片：

1. 跑 baseline 验证（记下"未改前"的所有测试结果，作为对照基线）
2. 机械性重构：改名、提取、合并、拆分（每步只动一类）
3. 每步后跑相同测试，对比 baseline
4. 评估是否触及长期约定（按 [doc-rewriting-rules.md](../doc-rewriting-rules.md) 检查）

## 实施 session 注意事项

- 每步只做一类重构（不要"改名 + 提取 + 改接口"一次完成）
- 每步后立即跑 baseline 测试 + diff
- 拒绝"顺手扩大"——`refactor-brief.md` 列出的"不动的文件"必须不动
- 不要在重构里加新功能（新功能 = 独立 task）

## 关联

- 通用 L2 三 Session 纪律：[l2-multi-session-runbook.md](./l2-multi-session-runbook.md)
- refactor 模板：[../templates/refactor-brief.md](../templates/refactor-brief.md)（含"行为不变量"必填字段）
- 任务分级：[../task-levels.md](../task-levels.md)
