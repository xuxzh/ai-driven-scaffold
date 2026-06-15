# 缺陷修复交付运行手册（bugfix-specific）

> **本文档只描述"缺陷修复（bugfix）"工作流相对通用 L2+ 纪律的差异**。通用 4 session 纪律见 [l2-multi-session-runbook.md](./l2-multi-session-runbook.md)。

## 范围

本文档适用于 L2+ 缺陷修复任务。L0 / L1 缺陷可直接修复（用 [bugfix-brief.md](../templates/bugfix-brief.md) 记录现象和假设）。

## L2+ bugfix 与 feature 的关键差异

- **设计 session 重点不同**：feature 关注"建议方案/备选方案"，bugfix 关注"复现面/可证伪假设/非目标"
- **实施 session 重点不同**：feature 关注"完整新功能 + 验证"，bugfix 关注"最小改动 + 回归测试"
- **评审 session 重点不同**：feature 关注"边界 / 行为回归"，bugfix 关注"复现面是否真覆盖 / 回归测试是否到位"
- **不需要"备选方案与拒绝理由"段**：bugfix 通常只有 1 个修复路径

## 推荐切片顺序

第 2 会话（计划）的任务切片建议按以下顺序拆分：

1. 写最小复现测试（验证 bug 真的存在）
2. 写最小修复（先让复现测试通过）
3. 跑回归测试（确认未引入新问题）
4. 评估是否触及长期约定（按 [doc-rewriting-rules.md](../doc-rewriting-rules.md) 检查）

## 实施 session 注意事项

- 优先用最接近行为控制处的文件作锚点
- 不要"顺手"重构附近代码（bugfix 改动最小化）
- 修复完成后跑回归，而不是只跑单测

## 关联

- 通用 L2+ 4 session 纪律：[l2-multi-session-runbook.md](./l2-multi-session-runbook.md)
- bugfix 模板：[../templates/bugfix-brief.md](../templates/bugfix-brief.md)
- 任务分级：[../task-levels.md](../task-levels.md)
