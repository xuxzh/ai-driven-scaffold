# AI 上下文索引

> 这是 AI 新会话进入仓库时的导航地图。它不替代具体 spec、plan 或 runbook，只聚合稳定入口和判断顺序。

## 阅读路径

### 3 分钟短路径（L0 / L1 单 session 用）

用于 `L0`、低风险 `L1`、评审前快速定位或已经熟悉仓库的新会话。

1. `AGENTS.md`：仓库级高频规则和不可破坏的边界。
2. 本文件（context-index.md）：判断任务类型、阅读分支、代码锚点和验证入口。
3. [`docs/CONTEXT.md`](../CONTEXT.md)：术语表（"准入门禁 / 验证层 vs 准入层 / 角色边界 / verify 报告"等）
4. 当前任务对应入口：按下方"按任务类型分流"选择具体模板、Runbook、规范或代码锚点。

### 深路径（L2+ 多 session 用）

L2 任务按 [ADR-0003](../adr/0003-multi-session-l2.md) 串行 3 个 session（规划 / 实施 / 评审）；L3 任务将 L2 的"规划 Session"拆为"设计 / 计划"双 Session，并在实施 Session 启动前收用户明确批准信号（详见 [ADR-0005](../adr/0005-l3-approval-gate.md)）。每个 session 的阅读入口**按角色**分流——会话边界 = 角色边界，详见 [`docs/ai/ai-role-boundaries.md`](./ai-role-boundaries.md)。

#### L2 规划 session（设计辅助者 + 计划拆解者）
1. `AGENTS.md`（边界）
2. 本文件（context-index.md）
3. `docs/ai/task-levels.md`（确认 L 级别）
4. `docs/ai/templates/feature-spec.md`（spec 模板）
5. `docs/ai/templates/implementation-plan.md`（plan 模板；先写 spec → 用户确认 → 再写 plan）
6. `docs/adr/0004-l2-spec-and-plan.md`（spec/plan 内容分工 + 物理分离硬门禁）
7. `docs/ai/verification-baseline.md`（plan 切片的 verify 命令从这里推导）

#### L2 实施 session（实施者 + 文档维护者）
1. `AGENTS.md`（边界 + Adoption Profile 里的 verify 命令定义）
2. 上一 session 交付物：`docs/specs/...` + `docs/plans/...` 双份（**始终是两份独立文件**）
3. `docs/ai/branch-strategy.md`（分支 / worktree 选择）
4. `docs/ai/ai-role-boundaries.md`（实施者 + 文档维护者的合并依据与边界）
5. `docs/adr/0002-verify-hard-gate.md`（verify 必跑 + 必汇报 + 缺信号停在未完成）
6. **必须**跑 `verify` 并写入 `## 验证证据` 段（命令 / 退出码 / 关键输出摘要 / 未跑项）

#### L2 评审 session（审查者，**默认新开 session**）
1. `AGENTS.md`（边界）
2. 上一 session 交付物：`git diff <base>..HEAD` + spec + plan + `## 验证证据` 段
3. `docs/ai/checklists/review-checklist.md`（评审清单）
4. `docs/adr/0003-multi-session-l2.md`（评审独立性 + session 默认新开 + spec/plan 物理分离硬门禁）
5. `docs/adr/0002-verify-hard-gate.md`（verify 必跑纪律检查）
6. **不**预读实施 session 的中间对话
7. review report **必含**：测试盲区清单 + 未跑项确认 + spec/plan 物理分离 + spec 是否先经用户确认（详见 [`docs/CONTEXT.md`](../CONTEXT.md)）

#### L3 任务（4 Session + 实施前明确批准）

L3 任务在 L2 三 Session 之上把"规划 session"拆成"设计 + 计划"双 session，并在实施 session 启动前收用户"已批准"信号：

- **设计 session**（设计辅助者）：产出 spec；阅读入口同 L2 规划 session 步骤 1–6（但只写到 spec）
- **计划 session**（计划拆解者）：产出 plan；阅读入口 = `AGENTS.md` + 上一 session 交付物 spec + plan 模板 + verification-baseline
- **实施 session**：在 L2 实施 session 步骤之外，**额外**读 [ADR-0005](../adr/0005-l3-approval-gate.md)；缺批准信号时不得跑 `git add` / `git commit` / patch / push
- **评审 session**：在 L2 评审 session 步骤之外，额外核对 `## 批准` 段（批准信号 + 范围 + 引用 spec/plan 路径）

L2 与 L3 都不允许规划者把 spec 与 plan 合并为一份文件；两者必须始终物理分离。L2 只允许设计辅助者与计划拆解者合并在同一规划 session，L3 则必须拆分为设计与计划两个 Session。

## 单点定义（核心规则）

以下文件承载本脚手架的核心治理规则，请按需查阅：

| 关注点 | 文档 |
|---|---|
| L0/L1/L2/L3 任务分级 | [task-levels.md](./task-levels.md) |
| 完成定义 | [completion-criteria.md](./completion-criteria.md) |
| 验证基线 | [verification-baseline.md](./verification-baseline.md) |
| 分支与 worktree 策略 | [branch-strategy.md](./branch-strategy.md) |
| AI 角色边界 | [ai-role-boundaries.md](./ai-role-boundaries.md) |
| 文档回写规则 | [doc-rewriting-rules.md](./doc-rewriting-rules.md) |
| spec / plan 命名与元信息 | [spec-and-plan-naming.md](./spec-and-plan-naming.md) |

## 主要代码锚点（按任务方向）

> 以下表是**示例占位**。每个项目应在 `AGENTS.md` 的 "用户项目元信息（Adoption Profile）" 段落维护本项目的真实锚点；本文件不维护第二份项目元信息。

| 任务方向 | 优先阅读锚点 |
|---|---|
| 入口 / 启动流程 | `<entry-file>`（用户在 AGENTS.md Adoption Profile 标注的实际入口） |
| 数据访问 | `<data-access-dir>`（如 `src/services/`, `internal/api/`） |
| 共享基础设施 | `<shared-pkg-dir>`（如 `packages/`, `internal/`, `libs/`） |
| 配置 / 环境 | `<config-dir>`（如 `config/`, `env/`, `.env.example`） |
| 测试 | `<test-dir>`（如 `tests/`, `__tests__/`, `*_test.go`） |
| E2E | `<e2e-dir>`（如 `e2e/`, `tests/e2e/`） |
| 文档 | `docs/`（包含 `ai/`, `adr/`, `specs/`, `plans/`, `standards/`） |

## 任务入口（按任务类型分流）

| 任务类型 | 阅读入口 | 执行要求 |
|---|---|---|
| `L0` 文案、注释、局部测试修复 | `AGENTS.md`、本文件、相关代码锚点 | 可直接做；必须运行与改动直接相关的最小验证。 |
| `L1` 单目标常规改动 | [task-packet.md](./templates/task-packet.md)、相关规范和代码锚点 | 先明确目标、锚点、假设、验证和非目标，再实施。 |
| `L2` 跨文件行为、数据流或入口变化 | [task-levels.md](./task-levels.md)、[feature-spec.md](./templates/feature-spec.md) 和 [implementation-plan.md](./templates/implementation-plan.md) | 先按 spec 模板写 spec → 用户确认 → 按 plan 模板写 plan → 进入实施；spec 与 plan **始终是两份独立文件**，无规模豁免；走 L2 三 Session（规划 / 实施 / 评审，详见 [l2-multi-session-runbook.md](./runbooks/l2-multi-session-runbook.md)） |
| 业务功能 + API/UI 原型 | [l2-multi-session-runbook.md](./runbooks/l2-multi-session-runbook.md) + [feature-delivery-runbook.md](./runbooks/feature-delivery-runbook.md) | 按 spec、plan、可验证切片推进。 |
| 缺陷修复 | [bugfix-brief.md](./templates/bugfix-brief.md) / [bugfix-delivery-runbook.md](./runbooks/bugfix-delivery-runbook.md) | L0/L1 走 bugfix-brief；L2 走通用 3 session + bugfix-specific；L3 走 4 session + 实施前明确批准 + bugfix-specific。 |
| 重构 | [refactor-brief.md](./templates/refactor-brief.md) / [refactor-delivery-runbook.md](./runbooks/refactor-delivery-runbook.md) | L0/L1 走 refactor-brief；L2 走通用 3 session + refactor-specific；L3 走 4 session + 实施前明确批准 + refactor-specific。 |
| 评审 | [review-checklist.md](./checklists/review-checklist.md) | 先找行为回归、边界破坏、验证缺失和测试缺口；review report 必含测试盲区 + 未跑项确认。 |
| `L3` CI、依赖、鉴权、安全、跨 workspace、仓库级约定 | [task-levels.md](./task-levels.md)、[ADR-0005](../adr/0005-l3-approval-gate.md) | 人工主导；先查验正式 spec 和 plan 双份 + 实施 session 启动前收"已批准"信号；AI 只做分析、草案、验证辅助和明确批准范围内的受控 patch。 |

## 进入实现前准入门禁

AI 进入实质性编辑前，必须先满足以下准入条件：

- 任何代码改动前，先说明任务级别：`L0`、`L1`、`L2` 或 `L3`（详见 [task-levels.md](./task-levels.md)）
- 当前分支检查：不得在 `main` / `master` 直接编辑或提交开发改动（详见 [branch-strategy.md](./branch-strategy.md)）
- 分支与 worktree 选择：默认策略由 [branch-strategy.md](./branch-strategy.md) 的等级矩阵决定；本索引不重复定义
- 主锚点文件：最接近行为控制处的文件或符号
- 非目标：本次明确不改的行为、模块或文档
- 最小验证命令：能证明当前切片成立的最窄检查
- 是否需要 spec/plan：`L2` 及以上必须先查验正式 spec 和 plan 双份，`L1` 至少需要 task packet
- 正式 spec 和 plan 统一位于 `docs/specs/`、`docs/plans/`；聊天计划、临时 TODO、`update_plan` 输出不算正式文档
- 用户明确指定 `L2` 或 `L3` 时，AI 无权自行降级；如分级存在争议，按更高风险级别处理
- `L3` 不允许被当作普通 `L2` 直接执行，必须明确人工主导和 AI 的批准边界；实施 session 启动前必须收"已批准"信号（详见 [ADR-0005](../adr/0005-l3-approval-gate.md)）
- 是否需要文档回写：触及长期边界、默认做法、验证路径或高频坑时需要（详见 [doc-rewriting-rules.md](./doc-rewriting-rules.md)）

## 验证入口

- 完整验证：项目根目录的 `verify` 命令（具体定义见 `AGENTS.md` 顶部"用户项目元信息"）
- 局部验证：按 [verification-baseline.md](./verification-baseline.md) 的分层基线选择最窄但足够的检查
- 基础命令：`<pm> lint`、`<pm> typecheck`、`<pm> test`、`<pm> build`（其中 `<pm>` 是项目实际包管理器）

AI 汇报时必须说明实际运行了哪些命令、哪些通过、哪些未运行及原因。

## 文档回写规则

详见 [doc-rewriting-rules.md](./doc-rewriting-rules.md)。简要复述：

- 改动改变长期边界、默认做法或验证路径 → 回写
- 修复暴露出未来高概率重复出现的坑 → 回写
- 新增或拒绝某个会影响后续 AI 判断的长期决策 → 回写
- CI、部署、依赖、安全或环境行为发生变化 → 回写

判断依据进入 `docs/specs/`、`docs/adr/`、`docs/ai/runbooks/`、`docs/ai/checklists/` 或 `AGENTS.md`，不要只留在聊天记录里。
