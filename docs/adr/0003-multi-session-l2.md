# ADR-0003 L2+ 任务强制多 session 串行（设计 / 计划 / 实施 / 评审）

日期：2026-06-15
适用等级：L2 / L3

## 状态

Proposed

## 背景

`ai-role-boundaries.md` 推荐 5 个 AI 角色（设计辅助者 / 计划拆解者 / 实施者 / 审查者 / 文档维护者），并明确"应避免一次会话同时做所有事情"。但 `feature-delivery-runbook.md` 的 8 步流程**实际假设一个 AI session 完整跑完**——"AI 开始前的必读入口"按 session 切，第 1 步写 spec、第 2 步写 plan、第 3-7 步实施、第 8 步评审，全在一个会话里推进。

这与 5 角色模型是直接矛盾的：实施者自己写完代码再切到审查者，**几乎不会找出自己的回归和测试缺口**。governance-core.md 自己列的评审顺序是"行为回归 / 边界破坏 / 验证缺失 / 测试缺口 / 风格与可读性"——这些都需要**外部视角**才能稳准狠挑出来。

更具体地：

- 软推荐"区分角色"在文档中讲了 4 个月，但 runbook 实际从 1 个 session 出发，所有角色由同一个上下文串成
- 实施 session 内的"自审"会**优先合理化已有 patch**，与 ADR-0002 的 verify 必汇报纪律叠加后，问题被"已 verify"覆盖
- L2 任务的 spec / plan / 实施 / 评审 实际是 4 份独立交付物，但被一个 session 串起来后，交付物之间的"交接"在文档里看不到

## 决策

L2+ 任务**必须**按"设计 / 计划 / 实施 / 评审" 4 个独立 session 串行推进。每 session 的输入、产出、必跑 verify 与交接物如下：

| Session | 必读输入 | 必交付物 | 必跑 verify |
|---|---|---|---|
| **设计** | `AGENTS.md`、`context-index.md`、`task-levels.md`、项目接口/UI 文档 | `docs/specs/<date>-<name>.md`（仅 spec） | 不要求；spec 阶段 verify 由 plan session 触发 |
| **计划** | 设计 session 产出的 spec | `docs/plans/<date>-<name>.md` | 不要求；verify 由实施 session 触发 |
| **实施** | 设计产出的 spec + 计划产出的 plan | 代码改动 + 测试 + `## 验证证据` 段 | **必须跑 `verify` 并写入汇报**（继承 ADR-0002） |
| **评审** | 实施 session 的代码 + `## 验证证据` 段；建议从**新开 session** 开始，不读实施 session 的中间对话 | `review report`（按 `review-checklist.md` 结构） | 必含"测试盲区"与"未跑项"清单 |

L2+ 任务的会话边界是**角色边界**：

- 设计 session = 设计辅助者
- 计划 session = 计划拆解者
- 实施 session = 实施者 + 文档维护者（合并：实施过程中的文档回写是实施的一部分）
- 评审 session = 审查者

### 硬约束范式（可选）

按 ADR-0002 沉淀的"硬约束三件套"句式落地：

> **在 (开始下一 session) 之前**，AI 必须 **(从仓库文档读取上一 session 交付物，而非依赖会话历史)**；**汇报 (本次 session 必交付物)** 于 (spec / plan / 验证证据 / review report)；**缺 (上一 session 完成信号) 时 AI 必须停在 (等待用户确认状态)**。

具体的强制规则：

1. **新 session 不允许依赖会话历史推断上一 session 意图**——必须从仓库内 `docs/specs/`、`docs/plans/`、`## 验证证据` 段读取
2. **评审 session 默认开新 session**（在 `.claude/hooks/` 或外部触发），且**不**预读实施 session 的中间对话；只读 `git diff <base>..HEAD`、spec、plan、`## 验证证据`
3. **每个 session 结束前必须显式输出"本 session 完成信号"**（一段文字"设计 session 完成，交付物：spec at <path>"），下一 session 看到该信号才能开始
4. **L0 / L1 任务保持单 session**——多 session 是 L2+ 的入场费，不向下传递到 L1
5. **小 L2 例外**：若 L2 任务规模 < 半天（用户判断），可申请把"设计 + 计划"合并为 1 session，但仍需"实施 + 评审"分离；此例外需在 spec 顶部标注 `## 快速通道` 段

## 后果

- 正向影响：
  - 实施者自审盲点被新 session 的"零上下文"消除；reviewer session 看到的只有交付物，没有合理化路径
  - 4 份独立交付物（spec / plan / 验证证据 / review report）都进仓库；知识沉淀更厚
  - 与 ADR-0002 的 verify 必跑天然契合：每 session 跑一次 verify
  - 与 ADR-0004 的 spec + plan 都写衔接：双 session（设计 + 计划）让 spec 与 plan 的分离变得自然
  - 与 ADR-0005 的 L3 审批门禁衔接：L3 在多 session 框架下加入"实施 session 启动前必须收用户批准"信号
- 约束或成本：
  - L2+ 任务的完成时间被切碎：单 session 不再能 30 分钟结束一个 L2
  - 实施 session 之外的 3 个 session 都需要"重新读仓库上下文"——这本身是开销
  - 用户需要主动管理会话切换；如果只在 1 个 session 内"假装"换了角色，治理失效
  - 小 L2 的快速通道例外需要 spec 顶部声明；这是新增的轻量流程
- 后续触发条件：
  - 若 `.claude/hooks/` 引入 session boundary 提示（如 `PreCompact` / `SessionStart`），本 ADR 的"必读上一 session 产出"可由 hook 强制读取而非依赖 AI 自律
  - 若 `docs/specs/` / `docs/plans/` 出现大量"快速通道"标注且频繁触发，需要评估"快速通道"是否被滥用为绕过入口
  - 若评审 session 的"测试盲区清单"被实施 session 反驳，需要回到本 ADR 评估是否要引入"评审独立性"硬约束

## 关联

### 前置 ADR

- [ADR-0001](0001-task-level-governance.md)：本 ADR 的 "L2+" 作用域来自其分级模型。
- [ADR-0002](0002-verify-hard-gate.md)：本 ADR 继承其"硬约束三件套"句式；实施 session 的 verify 必跑继承自 ADR-0002。

### 后续 ADR

- [ADR-0004](0004-l2-spec-and-plan.md)：L2 任务默认 spec + plan 双份作为硬门禁；本 ADR 的"设计 + 计划"双 session 与之衔接。
- [ADR-0005](0005-l3-approval-gate.md)：L3 任务叠加 Pre-Implementation Approval Gate；本 ADR 的多 session 框架为其提供 session 切换点。

### 基线文档

- [../ai/ai-role-boundaries.md](../ai/ai-role-boundaries.md)

### 其它

- Runbook：[../ai/runbooks/l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md)（2026-06-15 拆分自原 `feature-delivery-runbook.md` 的通用 4 session 纪律；原 `feature-delivery-runbook.md` 收缩为 feature-specific 补充）
- 评审清单：[../ai/checklists/review-checklist.md](../ai/checklists/review-checklist.md)
- 上下文导航（待更新）：[../ai/context-index.md](../ai/context-index.md)
