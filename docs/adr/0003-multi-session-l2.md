# ADR-0003 L2 三 Session / L3 四 Session 串行（规划 / 实施 / 评审）

日期：2026-06-15
修订：2026-08-01（将 L2 收敛为"规划 / 实施 / 评审"三 Session；L3 在此之上叠加"设计 + 计划"双 Session + 实施前批准门禁）
适用等级：L2 / L3

## 状态

Accepted（Supersedes 2026-06-15 初版"4 session 串行"+ 2026-08-01 之前的"小 L2 快速通道合并 spec/plan 物理分离"例外；本 ADR 是当前治理基线的硬约束依据）

## 背景

`ai-role-boundaries.md` 推荐 5 个 AI 角色（设计辅助者 / 计划拆解者 / 实施者 / 审查者 / 文档维护者），并明确"应避免一次会话同时做所有事情"。但 `feature-delivery-runbook.md` 的早期 8 步流程**实际假设一个 AI session 完整跑完**——"AI 开始前的必读入口"按 session 切，第 1 步写 spec、第 2 步写 plan、第 3-7 步实施、第 8 步评审，全在一个会话里推进。

这与 5 角色模型是直接矛盾的：实施者自己写完代码再切到审查者，**几乎不会找出自己的回归和测试缺口**。governance-core.md 自己列的评审顺序是"行为回归 / 边界破坏 / 验证缺失 / 测试缺口 / 风格与可读性"——这些都需要**外部视角**才能稳准狠挑出来。

更具体地：

- 软推荐"区分角色"在文档中讲了 4 个月，但 runbook 实际从 1 个 session 出发，所有角色由同一个上下文串成
- 实施 session 内的"自审"会**优先合理化已有 patch**，与 ADR-0002 的 verify 必汇报纪律叠加后，问题被"已 verify"覆盖
- L2 任务的 spec / plan / 实施 / 评审 实际是 4 份独立交付物，但被一个 session 串起来后，交付物之间的"交接"在文档里看不到

ADR-0003 的 2026-06-15 初版要求 L2+ 强制按四 Session 串行，并额外允许"小 L2 快速通道"把"设计 + 计划"合并为 1 session，只豁免"spec 与 plan 物理分离"。但该规则在 2026-08-01 的复盘中发现三个反模式：

1. **会话切换的成本高于治理收益**——"设计"与"计划"职责在同一 session 内仍可由同一执行者先后承担，分两个 session 主要增加读仓库与交接信号成本，未必提高设计质量
2. **"快速通道物理合并 spec/plan"让 ADR-0004 的双文件交付可被绕过**——只要声明"小 L2"，spec 顶部加一段 `## 快速通道` 就能让 spec 与 plan 合并成一份文件，绕开了 ADR-0004 的物理分离门禁
3. **L3 与 L2 共用同一套 session 框架反而模糊了 L3 的实施前批准门禁**——L3 的"实施前明确批准"是 L2 之上叠加的额外约束，不应与 L2 的 session 串行在同一层级表述

## 决策

按任务等级区分 session 数：

| 等级 | Session 数 | Session 序列 | 额外门禁 |
|---|---|---|---|
| `L2` | 3 | 规划 / 实施 / 评审 | — |
| `L3` | 4 | 设计 / 计划 / 实施 / 评审 | **实施 session 启动前必须收用户明确批准**（[ADR-0005](0005-l3-approval-gate.md)） |

### L2 三 Session（规划 / 实施 / 评审）

| Session | 必读输入 | 必交付物 | 必跑 verify |
|---|---|---|---|
| **规划** | `AGENTS.md`、`context-index.md`、`task-levels.md`、项目接口/UI 文档 | `docs/specs/<date>-<name>.md`（仅 spec）+ `docs/plans/<date>-<name>.md`（仅 plan）；spec 必须先经用户确认后再写 plan | 不要求；verify 由实施 session 触发 |
| **实施** | 上一 session 产出的 spec + plan 双份 | 代码改动 + 测试 + spec/plan 文件的 `## 验证证据` 段 | **必须跑 `verify` 并写入汇报**（继承 ADR-0002） |
| **评审** | 实施 session 的代码 + `## 验证证据` 段；建议从**新开 session** 开始，不读实施 session 的中间对话 | `review report`（按 `review-checklist.md` 结构） | 必含"测试盲区"与"未跑项"清单 |

L2 任务的会话边界是**角色边界**：

- 规划 session = 设计辅助者 + 计划拆解者（合并依据：spec 与 plan 都是设计期交付物，输出相互依赖，且不修改业务代码；详见 `ai-role-boundaries.md` 的"角色合并原则"段）
- 实施 session = 实施者 + 文档维护者
- 评审 session = 审查者

**规划 session 的内部步骤**：先写 spec → 用户明确确认 → 再写 plan。spec 与 plan **始终是两份独立文件**，物理分离是硬门禁；spec 阶段不得提前写 plan 的实现切片，plan 阶段不得回填 spec 的设计决策。

### L3 四 Session（设计 / 计划 / 实施 / 评审）

| Session | 必读输入 | 必交付物 | 必跑 verify |
|---|---|---|---|
| **设计** | `AGENTS.md`、`context-index.md`、`task-levels.md`、项目接口/UI 文档 | `docs/specs/<date>-<name>.md`（仅 spec） | 不要求；spec 阶段 verify 由 plan session 触发 |
| **计划** | 设计 session 产出的 spec | `docs/plans/<date>-<name>.md` | 不要求；verify 由实施 session 触发 |
| **实施** | 设计产出的 spec + 计划产出的 plan | 代码改动 + 测试 + spec/plan 文件的 `## 验证证据` 段 + `## 批准` 段 | **必须跑 `verify` 并写入汇报**（继承 ADR-0002）；**必须先收用户"已批准"信号**（详见 [ADR-0005](0005-l3-approval-gate.md)） |
| **评审** | 实施 session 的代码 + `## 验证证据` 段 + `## 批准` 段；建议从**新开 session** 开始，不读实施 session 的中间对话 | `review report`（按 `review-checklist.md` 结构） | 必含"测试盲区"与"未跑项"清单，并核对批准范围 |

L3 任务的会话边界是**角色边界**：

- 设计 session = 设计辅助者
- 计划 session = 计划拆解者
- 实施 session = 实施者 + 文档维护者
- 评审 session = 审查者

### 硬约束范式（可选）

按 ADR-0002 沉淀的"硬约束三件套"句式落地：

> **在 (开始下一 session) 之前**，AI 必须 **(从仓库文档读取上一 session 交付物，而非依赖会话历史)**；**汇报 (本次 session 必交付物)** 于 (spec / plan / 验证证据 / review report)；**缺 (上一 session 完成信号) 时 AI 必须停在 (等待用户确认状态)**。

具体的强制规则：

1. **新 session 不允许依赖会话历史推断上一 session 意图**——必须从仓库内 `docs/specs/`、`docs/plans/`、`## 验证证据` 段读取
2. **评审 session 默认开新 session**（由人工或外部会话工具触发），且**不**预读实施 session 的中间对话；只读 `git diff <base>..HEAD`、spec、plan、`## 验证证据`
3. **每个 session 结束前必须显式输出"本 session 完成信号"**（一段文字"规划 session 完成，交付物：spec at <path> + plan at <path>"），下一 session 看到该信号才能开始
4. **L0 / L1 任务保持单 session**——多 session 是 L2+ 的入场费，不向下传递到 L1
5. **spec 与 plan 的物理分离不可豁免**：L2 任务无论规模，spec 与 plan 始终是两份独立文件；不存在"快速通道合并 spec/plan"的现行例外

> **已取代**：2026-06-15 初版 ADR-0003 规定的"L2+ 必须 4 个 session 串行 + 小 L2 可申请把'设计 + 计划'合并为 1 session"已被本修订取代。**当前规则为 L2 三 Session、L3 四 Session；spec 与 plan 始终物理分离。** 任何引用"L2+ 4 个 session"或"快速通道合并 spec/plan"的文档应视为过时，按本 ADR 修订。

> **已取代**：2026-06-15 初版 ADR-0003 第 5 条"小 L2 例外"（豁免 spec/plan 物理分离）已被本修订显式废止。`docs/specs/` 与 `docs/plans/` 永远是两份文件；spec 顶部 `## 快速通道` 段不再作为现行字段保留（详见 [feature-spec.md](../ai/templates/feature-spec.md) 的修订）。

## 后果

- 正向影响：
  - 实施者自审盲点被新 session 的"零上下文"消除；reviewer session 看到的只有交付物，没有合理化路径
  - L2 由 4 session 收敛为 3 session，session 切换与交接信号成本下降约 25%
  - spec 与 plan 物理分离成为不可豁免的硬门禁——绕开 ADR-0004 的物理合并例外不复存在
  - L3 的"设计 / 计划"双 session 仍是必要的：L3 涉及 CI / 依赖 / 仓库级约定，spec 与 plan 的内容分工需要更强的会话切换支撑
  - 与 ADR-0002 的 verify 必跑天然契合：每 session 跑一次 verify
  - 与 ADR-0004 的 spec + plan 都写衔接：L2 规划 session 内"先 spec 后 plan"的内部步骤自然落字
  - 与 ADR-0005 的 L3 审批门禁衔接：L3 在多 session 框架下加入"实施 session 启动前必须收用户批准"信号
- 约束或成本：
  - L2 任务仍需 3 session；完成时间比单 session 切碎
  - 实施 session 之外的 2（L2）/ 3（L3）个 session 都需要"重新读仓库上下文"——这本身是开销
  - 用户需要主动管理会话切换；如果只在 1 个 session 内"假装"换了角色，治理失效
- 后续触发条件：
  - 若后续引入工具无关的 session boundary 提示，本 ADR 的"必读上一 session 产出"可由外部机制强制读取而非依赖 AI 自律
  - 若 `docs/specs/` 顶部再次出现"快速通道"标注（即使被本 ADR 取代后），需要回到本 ADR 评估是否需要在 review checklist 加"反快速通道"检查项
  - 若评审 session 的"测试盲区清单"被实施 session 反驳，需要回到本 ADR 评估是否要引入"评审独立性"硬约束

## 关联

### 前置 ADR

- [ADR-0001](0001-task-level-governance.md)：本 ADR 的 "L2 / L3" 作用域来自其分级模型。
- [ADR-0002](0002-verify-hard-gate.md)：本 ADR 继承其"硬约束三件套"句式；实施 session 的 verify 必跑继承自 ADR-0002。

### 后续 ADR

- [ADR-0004](0004-l2-spec-and-plan.md)：L2 任务默认 spec + plan 双份作为硬门禁；本 ADR 的"L2 规划 session 内 spec 与 plan 物理分离"与之衔接。
- [ADR-0005](0005-l3-approval-gate.md)：L3 任务叠加 Pre-Implementation Approval Gate；本 ADR 的多 session 框架为其提供 session 切换点。

### 基线文档

- [../ai/ai-role-boundaries.md](../ai/ai-role-boundaries.md)
- [../ai/runbooks/l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md)（L2 三 Session 执行流程）

### 其它

- 评审清单：[../ai/checklists/review-checklist.md](../ai/checklists/review-checklist.md)
- 上下文导航：[../ai/context-index.md](../ai/context-index.md)
