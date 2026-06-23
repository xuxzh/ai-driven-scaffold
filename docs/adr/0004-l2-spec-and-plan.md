# ADR-0004 L2 任务默认 spec + plan 都写（修订 ADR-0001 L2 段）

日期：2026-06-15
适用等级：L2

## 状态

Accepted（Amends ADR-0001 L2 段）

## 背景

`ADR-0001` 决策段对 L2 的规定是：

> "`L2`：跨文件行为、路由、数据流、共享边界等中等风险改动，**必须先有正式 spec 或 plan**。"

`task-levels.md` L2 段保留了同样的"或"。但仓库内其他文档实际已经把 spec 与 plan 当作**两份独立交付物**处理：

- `feature-spec.md` 模板与 `implementation-plan.md` 模板**并列**存在
- `feature-delivery-runbook.md` 第 1 步"只做需求整理和 spec"、第 2 步"基于 spec 写 implementation plan"——**两者都写**
- `task-levels.md` L2 段同时引用两个模板

"或"的歧义带来两个具体问题：

1. **设计门槛可绕过**：用户可以只写 `implementation-plan.md`（执行切片）而省略 `feature-spec.md`（设计准入），让 L2 任务的"做不做"被"怎么做"覆盖。spec 形同虚设。
2. **职责不分**：spec 与 plan 解决的是不同问题——spec 解决"做不做、做什么、不做什么、影响哪些边界"，plan 解决"按什么步骤、什么顺序、什么验证"——但"或"让两者可以互换，进一步模糊了它们的边界。

而且，从 spec 与 plan 的内容互补性看：

| 内容项 | spec 必含 | plan 必含 |
|---|---|---|
| 背景 / 目标 / 非目标 | ✓ | — |
| 受影响边界（路由 / 数据流 / 状态 / 共享组件） | ✓ | — |
| 备选方案与拒绝理由 | ✓ | — |
| 风险与未决问题 | ✓ | — |
| 文件清单 | — | ✓ |
| 任务切片（按可验证切片拆分） | — | ✓ |
| 每切片的步骤 / 命令 / 预期结果 | — | ✓ |
| 验证计划 | 总体策略 | 具体命令 |

如果 L2 只写 plan，"备选方案 / 拒绝理由"等设计决策无处落字；如果 L2 只写 spec，"按什么步骤执行"无着落点。两者写才能让设计与执行**都留痕**。

## 决策

L2 任务**默认**必须 `docs/specs/<date>-<name>.md`（spec）与 `docs/plans/<date>-<name>.md`（plan）**双份就位**。本 ADR 修订 `ADR-0001` L2 段的"或"为"和"——具体修订范围仅限 `ADR-0001` 中关于 L2 的**该单句**：

> 原句："`L2`：跨文件行为、路由、数据流、共享边界等中等风险改动，**必须先有正式 spec 或 plan**。"
> 修订为："`L2`：跨文件行为、路由、数据流、共享边界等中等风险改动，**默认必须先有正式 spec 和 plan 双份**（详见 `ADR-0004`）。"

### 硬约束范式（可选）

按 ADR-0002 沉淀的"硬约束三件套"句式落地：

> **在 (进入实施 session) 之前**，AI 必须 **(从仓库读到 spec + plan 双份就位)**；**汇报 (双份文档的路径与状态)** 于 (verify 报告)；**缺 (任一份) 时 AI 必须停在 (回到设计 / 计划 session)**。

具体的强制规则：

1. **spec 与 plan 的内容边界**——按本 ADR 背景段表格的"必含列"分工；任一份缺关键字段，视为该份"未就位"
2. **顺序**：spec 先于 plan；plan 必须在 spec 完成后才开始写（与 ADR-0003 的"设计 session → 计划 session"对齐）
3. **修订 ADR-0001 的范围**：仅 L2 段的"或"→"和"；L0 / L1 / L3 段不被本 ADR 改动
4. **快速通道例外**：与 ADR-0003 一致——若 L2 任务规模 < 半天，可在 spec 顶部声明 `## 快速通道` 段并简述合并理由；**例外不豁免 spec**，只豁免"spec 与 plan 必须分两份"的物理分离
5. **L1 → L2 升级**：若 L1 `task-packet` 在执行中发现需升级为 L2，必须先把 packet 内容**展开为 spec + plan 双份**进入仓库，再继续实施；不允许"边写代码边补 spec"
6. **plan 必须引用 spec 的 `<date>-<name>` 标识**——plan 文件抬头必须有 `> 基于 spec：[docs/specs/<date>-<name>.md](...)` 一行，否则视为与 spec 失联

## 后果

- 正向影响：
  - L2 任务的"做不做 / 做什么"由 spec 锁定，"怎么做"由 plan 锁定；两者**不互相替代**
  - 与 ADR-0003 的"设计 session 出 spec / 计划 session 出 plan"自然衔接
  - 与 ADR-0002 的 verify 必跑衔接：plan 中"每切片的命令"直接成为 verify 报告的"实际跑的项"
  - 备选方案与拒绝理由被 spec 强制记录，未来 AI 不会反复重新建议被显式拒绝的方案（呼应 ADR 索引里"某个方案被明确拒绝"的触发条件）
- 约束或成本：
  - L2 任务的文档成本从 1 份升到 2 份
  - spec 与 plan 之间需要保持引用一致；维护成本上升
  - L1 → L2 升级时需要"展开 packet 为 spec + plan"——这是新增的中途流程
- 后续触发条件：
  - 若 `docs/specs/` 与 `docs/plans/` 出现大量"快速通道"标注且比例 > 50%，需评估 L2 阈值是否需要上调
  - 若 spec 与 plan 出现内容漂移（spec 改了 plan 没改，或反之），需要回到本 ADR 评估"是否需要在 CI 加双向链接检查"
  - 若 L1 → L2 升级频繁发生且展开过程被打断，需要评估 L1 阈值是否需要收紧

## 关联

### 前置 ADR

- [ADR-0001](0001-task-level-governance.md)：本 ADR 修订其 L2 段"或"为"和"。
- [ADR-0002](0002-verify-hard-gate.md)：本 ADR 继承其"硬约束三件套"句式。
- [ADR-0003](0003-multi-session-l2.md)：本 ADR 的"spec + plan 双份"与多 session 框架的"设计 + 计划"双 session 对齐。

### 后续 ADR

- [ADR-0005](0005-l3-approval-gate.md)：L3 任务在 spec + plan 双份基础上叠加 Pre-Implementation Approval Gate。

### 基线文档

- [../ai/task-levels.md](../ai/task-levels.md)（同步修订 L2 段）

### 其它

- 模板：[../ai/templates/feature-spec.md](../ai/templates/feature-spec.md)、[../ai/templates/implementation-plan.md](../ai/templates/implementation-plan.md)
- Runbook：[../ai/runbooks/l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md)（通用 4 session 纪律入口）
