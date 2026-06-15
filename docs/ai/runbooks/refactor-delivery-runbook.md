# 重构交付运行手册（refactor-specific）

> **本文档只描述"重构（refactor）"工作流相对通用 L2+ 纪律的差异**。通用 4 session 纪律见 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)。

## 范围

本文档适用于 L2+ 重构任务。L0 / L1 重构可单 session 串完（用 [refactor-brief.md](../templates/refactor-brief.md) 记录行为不变量）。

## L2+ refactor 与 feature 的关键差异

- **设计 session 必含"行为不变量"**：refactor 的核心是"行为不变"，必须明确"什么不能变"（[refactor-brief.md](../templates/refactor-brief.md) 模板已要求）
- **计划 session 重点不同**：feature 关注"切片与可验证性"，refactor 关注"主战场文件 + 不应被改动的文件"
- **实施 session 重点不同**：feature 关注"新行为是否成立"，refactor 关注"每一步都跑相同测试 + 与 baseline 对比"
- **评审 session 重点不同**：feature 关注"边界 / 新功能完整性"，refactor 关注"行为不变量是否真被守住 / 是否有'顺手扩大'"

## 推荐切片顺序

第 2 会话（计划）的任务切片建议按以下顺序拆分：

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

- 通用 L2+ 4 session 纪律：[l2-multi-session-runbook.md](./l2-multi-session-runbook.md)
- refactor 模板：[../templates/refactor-brief.md](../templates/refactor-brief.md)（含"行为不变量"必填字段）
- 任务分级：[../task-levels.md](../task-levels.md)
