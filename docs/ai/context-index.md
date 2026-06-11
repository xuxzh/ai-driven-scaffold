# AI 上下文索引

> 这是 AI 新会话进入仓库时的导航地图。它不替代具体 spec、plan 或 runbook，只聚合稳定入口和判断顺序。

## 阅读路径

### 3 分钟短路径

用于 `L0`、低风险 `L1`、评审前快速定位或已经熟悉仓库的新会话。

1. `AGENTS.md`：仓库级高频规则和不可破坏的边界。
2. 本文件（context-index.md）：判断任务类型、阅读分支、代码锚点和验证入口。
3. 当前任务对应入口：按下方"按任务类型分流"选择具体模板、Runbook、规范或代码锚点。

### 深路径

用于 `L2`、`L3`、新功能、跨边界改动、业务功能或对仓库不熟悉的新会话。

1. `docs/ai/README.md`：AI 开发日常入口、任务级别和完成定义。
2. `docs/ai/governance-core.md`：治理基线与单点索引。
3. `docs/adr/README.md`：长期决策索引；只打开与当前任务相关的 ADR。
4. `docs/ai/runbooks/development-runbook.md`：常见执行陷阱和验证习惯。
5. `docs/ai/runbooks/feature-delivery-runbook.md`：业务功能分步交付流程。
6. 按任务需要读取对应的 spec、plan、规范或代码锚点。

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

## 主要代码锚点（按任务方向）

> 以下表是**示例占位**。每个项目应在 `AGENTS.md` 底部"用户项目元信息"段落维护本项目的真实锚点。

| 任务方向 | 优先阅读锚点 |
|---|---|
| 入口 / 启动流程 | `<entry-file>`（用户在 AGENTS.md 标注的实际入口） |
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
| `L2` 新功能、跨文件行为、数据流或入口变化 | [task-levels.md](./task-levels.md)、[feature-spec.md](./templates/feature-spec.md) 或 [implementation-plan.md](./templates/implementation-plan.md) | 先写正式 spec 或 plan，再进入实现；AI 不得自行降级。 |
| 业务功能 + API/UI 原型 | [feature-delivery-runbook.md](./runbooks/feature-delivery-runbook.md) | 按 spec、plan、可验证切片推进。 |
| 缺陷修复 | [bugfix-brief.md](./templates/bugfix-brief.md) | 先写现象、预期和假设。 |
| 评审 | [review-checklist.md](./checklists/review-checklist.md) | 先找行为回归、边界破坏、验证缺失和测试缺口。 |
| `L3` CI、依赖、鉴权、安全、仓库级约定 | [task-levels.md](./task-levels.md)、相关 ADR | 人工主导；先查验正式 spec 或 plan，AI 只做分析、草案、验证辅助和明确批准范围内的受控 patch。 |

## 进入实现前准入门禁

AI 进入实质性编辑前，必须先满足以下准入条件：

- 任何代码改动前，先说明任务级别：`L0`、`L1`、`L2` 或 `L3`（详见 [task-levels.md](./task-levels.md)）
- 当前分支检查：不得在 `main` / `master` 直接编辑或提交开发改动（详见 [branch-strategy.md](./branch-strategy.md)）
- 分支与 worktree 选择：默认使用任务分支；并行任务、长任务、`L2/L3` 或高风险改动优先使用 `.worktrees/` 下的 worktree
- 主锚点文件：最接近行为控制处的文件或符号
- 非目标：本次明确不改的行为、模块或文档
- 最小验证命令：能证明当前切片成立的最窄检查
- 是否需要 spec/plan：`L2` 及以上必须先查验正式 spec 或 plan，`L1` 至少需要 task packet
- 正式 spec 和 plan 统一位于 `docs/specs/`、`docs/plans/`；聊天计划、临时 TODO、`update_plan` 输出不算正式文档
- 用户明确指定 `L2` 或 `L3` 时，AI 无权自行降级；如分级存在争议，按更高风险级别处理
- `L3` 不允许被当作普通 `L2` 直接执行，必须明确人工主导和 AI 的批准边界
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
