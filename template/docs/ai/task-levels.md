# 任务分级 L0 / L1 / L2 / L3

> **这是单点定义文件**。所有其他文档（AGENTS.md、governance-core、runbook、checklist）应链接到此文件，而不是各自复述分级规则。

## TL;DR

- **判定三问**（任一为"是"即升级）：①是否改变用户可见行为？②是否跨越已有边界（共享 utility / 入口装配 / 仓库级规则）？③是否触及基础设施或仓库级约定（CI / 依赖 / 安全 / 鉴权）？
- **等级**：`L0` 单文件不改默认行为 → `L1` 单目标常规 → `L2` 跨文件行为 / 数据流 → `L3` CI / 依赖 / 安全 / 仓库级（人工主导 + 实施前批准）。
- **降级禁止**：用户指定 `L2` / `L3` 时 AI 不得降级；有争议按更高一级。

## 目的

为控制 AI 改动风险，仓库内工作按变更范围和行为影响分为 `L0`、`L1`、`L2`、`L3` 四级。分级的目的不是增加流程，而是让开发开始前就能明确应走的路径。

任何代码改动前，AI 必须先说明当前变更级别。用户明确指定 `L2` 或 `L3` 时，AI 无权自行降级；如分级存在争议，默认按更高风险级别处理。

主分支保护是进入实现前的通用准入条件。`main` / `master` 只作为稳定集成分支，不直接承载开发提交；实质性编辑前必须先进入任务分支或隔离 worktree。具体工作方式见 [branch-strategy.md](./branch-strategy.md)。

## 进入实现前准入门禁

AI 进入实质性编辑前，必须先满足以下准入条件：

- 任何代码改动前，先说明任务级别：`L0`、`L1`、`L2` 或 `L3`（见上方等级矩阵）
- 当前分支检查：不得在 `main` / `master` 直接编辑或提交开发改动（详见 [branch-strategy.md](./branch-strategy.md)）
- 分支与 worktree 选择：默认策略由 [branch-strategy.md](./branch-strategy.md) 的等级矩阵决定
- 主锚点文件：最接近行为控制处的文件或符号
- 非目标：本次明确不改的行为、模块或文档
- 最小验证命令：能证明当前切片成立的最窄检查（按 [verification-baseline.md](./verification-baseline.md) 分层基线）
- 是否需要 spec/plan：`L2` 及以上必须先查验正式 spec 和 plan 双份（详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)），`L1` 至少需要 task packet
- 正式 spec 和 plan 统一位于 `docs/specs/`、`docs/plans/`；聊天计划、临时 TODO、`update_plan` 输出不算正式文档
- 用户明确指定 `L2` 或 `L3` 时，AI 无权自行降级；如分级存在争议，按更高风险级别处理
- `L3` 不允许被当作普通 `L2` 直接执行，必须明确人工主导和 AI 的批准边界；实施 session 启动前必须收“已批准”信号（详见 [ADR-0005](../adr/0005-l3-approval-gate.md)）
- 是否需要文档回写：触及长期边界、默认做法、验证路径或高频坑时需要（详见 [doc-rewriting-rules.md](./doc-rewriting-rules.md)）

## 等级矩阵（统一语义，权威定义）

> 下表为本仓库任务分级的**唯一权威定义**。AGENTS.md / template/AGENTS.md / runbook / checklist 只允许摘要与链接，不允许重新发明条件。

| 级别 | 范围与条件 | 文档准入 | 分支与 worktree |
|---|---|---|---|
| `L0` | 单文件、不跨模块、不改变默认行为 | 无需 packet / spec / plan；至少运行最小验证 | 任务分支（worktree 可选，详见 [branch-strategy.md](./branch-strategy.md)） |
| `L1` | 单目标常规改动 | task packet 先行（[task-packet.md](./templates/task-packet.md)） | 任务分支 **+** 独立 worktree |
| `L2` | 跨文件行为、数据流或入口变化 | spec **+** plan 双文件（[feature-spec.md](./templates/feature-spec.md) / [implementation-plan.md](./templates/implementation-plan.md)；详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)） | 任务分支 **+** 独立 worktree |
| `L3` | CI、依赖、安全、鉴权、仓库级约定；人工主导 | `L2` 条件 **+** 实施前明确批准（Pre-Implementation Approval Gate，详见 [ADR-0005](../adr/0005-l3-approval-gate.md)） | 任务分支 **+** 独立 worktree |

> 关于 session 数与多 session 串行的细节，由 [ADR-0003](../adr/0003-multi-session-l2.md) 与对应 runbook 权威定义；本文档不再保留过时的"L2+ 4 个 session"等表述。
>
> 关于工作区落盘、分支、提交、worktree 四个概念的区分，以及"Strict Isolation Profile"接入选项，详见 [branch-strategy.md](./branch-strategy.md)。

## L0：单文件、不跨模块、不改变默认行为

`L0` 允许直接执行，但**核心约束**如下（任一不满足即升级到更高等级）：

- 改动只在 1 个文件内
- 不触及共享边界（应用壳层、入口装配、根脚本、仓库级规则文件、shared utility）
- 不修改默认行为 / 公共类型签名 / props / 任何调用方的预期
- 不需要跨文件测试同步

典型 L0 场景：

- 1 个**非共享**文件内的文案 / 注释 / 拼写修正
- 1 个本地组件的样式微调
- 已有测试的 1 处断言修复
- 1 处**非共享**文件的类型错误修复
- 非共享文件内部实现重构（变量重命名、代码块重组），**前提是外部可见行为完全不变**

L0 红线（**不是** L0 的反例）：

- 触及共享边界（应用壳层、入口装配、根脚本、仓库级规则文件、shared utility）
- 修改 props / 默认行为 / 公共类型签名
- 跨 2 个及以上文件的改动（即使是"样式 + 测试"组合）
- 共享 utility 的 JSDoc / 注释修改（属于共享边界）
- 任何影响其他模块/进程/调用方的逻辑变化（即使是单文件）

L0 任务不需要 packet / spec / plan，但**仍**要求附带最小验证（与改动直接相关的检查）。L0 默认走任务分支，worktree 可选；不得在 `main` / `master` 直接落盘——关于"工作区落盘 / 分支 / 提交 / worktree"的区分详见 [branch-strategy.md](./branch-strategy.md)。

## L1：单目标常规改动

`L1` 允许在轻计划后执行。此类任务通常涉及 2 到 4 个文件，但不改变核心架构边界。典型场景：

- 在既有模式下新增一个展示块或派生交互
- 为已有入口补测试
- 在现有数据访问层中增加一个新的 service 方法

`L1` 必须先有 task packet，至少包含：

- 目标
- 锚点文件或符号
- 可证伪假设
- 最小验证命令
- 非目标

`L1` 模板见 [task-packet.md](./templates/task-packet.md)。`L1` 必须使用任务分支 **+** 独立 worktree，详见 [branch-strategy.md](./branch-strategy.md)。

## L2：跨文件行为、数据流或入口变化

`L2` **默认必须先有正式 spec 和 plan 双份都就位**后，再执行（详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)，本节按 ADR-0004 修订 ADR-0001 的"或"为"和"）。判断标准：

- 跨文件行为变更
- 跨目录改动
- 入口流转变化
- 数据流变化
- 状态边界调整
- 端到端预期变化
- 公共组件行为调整

对于 `L2`，文档准入不是可选流程，不允许让 AI 在没有完整约束时"边看边改"。必须先形成 spec（`docs/specs/`）和 plan（`docs/plans/`）双份正式文档，再进入实现阶段。

spec 与 plan 的内容分工：

- **spec** 必含：背景、目标、非目标、受影响边界、备选方案与拒绝理由、风险、验证计划
- **plan** 必含：文件清单、任务切片、每切片的步骤 / 命令 / 预期结果

plan 抬头必须 `> 基于 spec：[docs/specs/<date>-<name>.md](...)` 一行，否则视为与 spec 失联。

聊天计划、临时 TODO、`update_plan` 输出不算正式 spec，也不算正式 plan。

`L2` 必须使用任务分支 **+** 独立 worktree；多 session 串行的具体编排以 [ADR-0003](../adr/0003-multi-session-l2.md) 与对应 runbook 为准（本文件不再保留旧版 session 数描述）。

`L2` 模板见 [feature-spec.md](./templates/feature-spec.md) 和 [implementation-plan.md](./templates/implementation-plan.md)。具体执行方式见 [branch-strategy.md](./branch-strategy.md)。

## L3：CI、依赖、安全、鉴权、仓库级约定

`L3` 必须人工主导，AI 只作为分析和辅助工具。典型场景：

- CI 变更
- 依赖升级
- 部署策略调整
- 跨 workspace 重构
- 全局脚手架约定修改
- 安全相关逻辑
- 鉴权与环境配置改动
- 仓库级规范文件的大幅改动

`L3` 在满足 `L2` 及以上的正式文档准入外，还**必须**满足 **Pre-Implementation Approval Gate**（详见 [ADR-0005](../adr/0005-l3-approval-gate.md)）：

- L3 实施 session 启动前必须收用户**明确批准**信号（"已批准" / "approved" / "proceed" / "go-ahead" / "确认执行" 任一字眼）
- 批准信号必须引用具体的 spec / plan 路径
- 批准范围仅限 spec / plan 中显式声明的范围；超出范围的改动需要重新批准
- 缺信号时 AI **不得**跑 `git add` / `git commit` / 直接 patch / 创建 MR / 直接 push；必须显式输出"等待批准"信号

AI 可以参与生成方案、列出风险、起草 patch 或辅助 review，也可以在明确批准范围内提交受控 patch，但不能在未明确批准的情况下自行推进实现。

`L3` 必须使用任务分支 **+** 独立 worktree；多 session 串行的具体编排以 [ADR-0003](../adr/0003-multi-session-l2.md) 与对应 runbook 为准。具体执行方式见 [branch-strategy.md](./branch-strategy.md)。

## 分级判断顺序

任务分级按以下顺序判断：

1. 是否改变用户可见行为
2. 是否跨越已有边界
3. 是否触及基础设施或仓库级约定

只要答案中出现"是"，任务就向更高一级提升。AI 无权自行把任务降级；如有争议，按更高一级处理。

## 关联

- 治理基线：[governance-core.md](./governance-core.md)
- 分支与 worktree：[branch-strategy.md](./branch-strategy.md)
- ADR：[../adr/0001-task-level-governance.md](../adr/0001-task-level-governance.md)、[../adr/0003-multi-session-l2.md](../adr/0003-multi-session-l2.md)、[../adr/0004-l2-spec-and-plan.md](../adr/0004-l2-spec-and-plan.md)、[../adr/0005-l3-approval-gate.md](../adr/0005-l3-approval-gate.md)