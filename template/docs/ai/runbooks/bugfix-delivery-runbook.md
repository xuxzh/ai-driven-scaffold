# 缺陷修复交付运行手册（bugfix-specific）

> **本文档只描述"缺陷修复（bugfix）"工作流相对通用 L2 三 Session 纪律的差异**。通用 L2 三 Session 纪律见 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)。

## 范围

本文档适用于 L2+ 缺陷修复任务。L0 / L1 缺陷可直接修复（用 [bugfix-brief.md](../templates/bugfix-brief.md) 记录现象和假设）。

> **已取代**：本 runbook 早前版本的"L2+ 强制 4 session"措辞已被 [ADR-0003](../../adr/0003-multi-session-l2.md) 2026-08-01 修订取代。**L2 现行规则是"规划 / 实施 / 评审"三 Session；spec 与 plan 始终是两份独立文件。**

## L2+ bugfix 与 feature 的关键差异

- **规划 session 重点不同**：feature 关注"建议方案/备选方案"，bugfix 关注"复现面/可证伪假设/非目标"
- **实施 session 重点不同**：feature 关注"完整新功能 + 验证"，bugfix 关注"最小改动 + 回归测试"
- **评审 session 重点不同**：feature 关注"边界 / 行为回归"，bugfix 关注"复现面是否真覆盖 / 回归测试是否到位"
- **不需要"备选方案与拒绝理由"段**：bugfix 通常只有 1 个修复路径

### verify 落点（与通用 L2 三 Session 纪律一致）

bugfix 任务也遵守 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md) 的"verify 落点细则"：

- 实施 session 必须跑项目根目录 `verify`，**同时**写入 `docs/specs/<date>-<name>.md` **与** `docs/plans/<date>-<name>.md` 双份末尾的 `## 验证证据` 段
- 规划 session **不**跑 verify、**不**写 `## 验证证据` 段，仅接力 spec + plan 双份
- **不接受**"只写 spec 或只写 plan"——双份均必填

### L3 bugfix（Pre-Implementation Approval Gate）

L3 bugfix 任务额外遵守 [ADR-0005](../../adr/0005-l3-approval-gate.md)：

- 实施 session 启动前必须收用户"已批准"信号并引用 spec / plan 双份路径
- `## 批准` 段（含第 8 项最小必含）必须位于 spec 与 plan 双份的 `## 验证证据` 段**之前**
- 批准**不得**跨任务复用——每个 bugfix 任务独立走"spec + plan + 批准"全流程

## 规划 session 内的推荐切片顺序

规划 session 写 plan 时，建议按以下顺序拆分任务切片：

1. 写最小复现测试（验证 bug 真的存在）
2. 写最小修复（先让复现测试通过）
3. 跑回归测试（确认未引入新问题）
4. 评估是否触及长期约定（按 [doc-rewriting-rules.md](../doc-rewriting-rules.md) 检查）

## 实施 session 注意事项

- 优先用最接近行为控制处的文件作锚点
- 不要"顺手"重构附近代码（bugfix 改动最小化）
- 修复完成后跑回归，而不是只跑单测

## 关联

- 通用 L2 三 Session 纪律：[l2-multi-session-runbook.md](./l2-multi-session-runbook.md)
- bugfix 模板：[../templates/bugfix-brief.md](../templates/bugfix-brief.md)
- 任务分级：[../task-levels.md](../task-levels.md)
