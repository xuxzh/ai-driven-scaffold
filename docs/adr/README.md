# ADR

这个目录用于记录长期有效的技术决策。单次任务设计继续放在 `../specs/`，可执行计划继续放在 `../plans/`。

## 索引

- [0001 使用任务分级治理 AI 改动风险](0001-task-level-governance.md)
- [0002 将 verify 升级为 AI 必跑 + 必汇报的硬门禁](0002-verify-hard-gate.md)
- [0003 L2+ 任务强制多 session 串行（设计 / 计划 / 实施 / 评审）](0003-multi-session-l2.md)
- [0004 L2 任务默认 spec + plan 都写（修订 ADR-0001 L2 段）](0004-l2-spec-and-plan.md)
- [0005 L3 任务 Pre-Implementation Approval Gate（L3 实施 session 启动前必须收用户批准）](0005-l3-approval-gate.md)

## 何时新增 ADR

当某个决定会长期影响后续 AI 或人工开发判断时，新增 ADR。典型场景包括：

- 仓库级流程、验证或目录职责发生变化
- 架构边界、入口装配顺序、数据访问路径等长期约定被确立或调整
- 某个方案被明确拒绝，且未来 AI 可能反复重新建议

新增 ADR 时使用 [adr-template.md](./adr-template.md) 作为结构骨架。

单次任务的设计背景继续放在 `../specs/`，执行步骤继续放在 `../plans/`。
