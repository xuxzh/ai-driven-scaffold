# ADR-NNNN 标题

日期：YYYY-MM-DD
适用等级：L0 | L1 | L2 | L3 | 全部

> 若适用等级为多选，写法如 `L1 / L2 / L3`；多选表示"凡触及任一等级的任务均受本 ADR 约束"。

## 状态

Proposed | Accepted | Amended | Superseded | Deprecated

> Amended = 已被局部修订（仍生效，需配合 ## 修订记录 读）
> Superseded = 已被整体取代（仍可参考历史，但不作为现行约束）
> Deprecated = 概念已废止（保留仅作历史索引）

## 修订记录

- YYYY-MM-DD：触发 ADR [NNNN](NNNN-...)，变更类型（局部修订 / 整体取代 / 概念废止），摘要一句话。

> 本段在状态为 Proposed / Accepted 时可留空，但若状态进入 Amended / Superseded / Deprecated 必含。

## 背景

说明为什么需要做这个长期决策，以及它影响哪些后续判断。
若决策涉及多个备选方案的取舍，将被拒方案及理由写在本段（与 MADR 的 "Considered Alternatives" 同位）。

## 决策

用明确、可执行的语言描述最终选择。

### 硬约束范式（可选）

> **在 (触发条件) 之前**，AI 必须 **(强制动作)**；**汇报 (汇报字段)** 于 (汇报位置)；**缺 (信号) 时 AI 必须停在 (状态)**。

适用于"AI 在某条件下必须做某事"类约束（参见 ADR-0002 的范式起源）。定义性 ADR（任务分级、术语定义、目录职责等）跳过此子段。

## 后果

- 正向影响：
- 约束或成本：
- 后续触发条件：

## 关联

### 前置 ADR（若有则必含）

- [ADR-NNNN](NNNN-...)：本 ADR 依赖其结论。

> 列表为空表示这是首批 ADR（如 ADR-0001）。

### 后续 ADR（可选）

- [ADR-NNNN](NNNN-...)：本 ADR 触发的后续决定。

### 基线文档（可选）

- [../ai/<name>.md](../ai/<name>.md)：本 ADR 修订或强化的单点定义。

### 其它（可选）

- 模板：[../ai/templates/<name>.md](../ai/templates/<name>.md)
- 清单：[../ai/checklists/<name>.md](../ai/checklists/<name>.md)
- Runbook：[../ai/runbooks/<name>.md](../ai/runbooks/<name>.md)
- 上下文导航：[../ai/context-index.md](../ai/context-index.md)
- 关联 spec（若本 ADR 实施对应某个具体 spec）：[docs/specs/<date>-<name>.md](../specs/<date>-<name>.md)
- 关联 plan（若本 ADR 实施对应某个具体 plan）：[docs/plans/<date>-<name>.md](../plans/<date>-<name>.md)
