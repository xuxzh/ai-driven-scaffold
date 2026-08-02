# 分支与 worktree 策略

> **这是单点定义文件**。所有改动前的分支检查、worktree 选择、命名约定都按此文件。任务等级矩阵见 [task-levels.md](./task-levels.md)。

## 四个概念的区分

本仓库的"工作区落盘 / 分支 / 提交 / worktree"是四个独立概念，必须区分清楚：

| 概念 | 含义 | 谁负责创建 / 切换 | 隔离粒度 |
|---|---|---|---|
| **工作区落盘** | 当前 checkout 的物理目录里的文件修改（编辑器保存、命令写入） | AI / 开发者 | 文件级 |
| **分支**（branch） | `git` 上的引用（`refs/heads/<name>`），决定 `HEAD` 指向哪条线 | 开发者（推荐通过任务分支规范创建） | 提交级 |
| **提交**（commit） | 在某条分支上的一次快照；`git commit` 产生 | 开发者 | 一次性 |
| **worktree** | 同一仓库的额外工作区副本（`.worktrees/<branch>/`），可在不打断主工作区的情况下独立编辑、构建、验证 | 开发者（`git worktree add` 或工具脚本） | 物理工作区级 |

常见误解：

- "切换分支"≠"创建 worktree"：切换分支只是把 `HEAD` 移到另一条线，**还在同一个工作区**；worktree 是另开一份物理工作区
- "提交"≠"分支合并"：commit 只是把改动落到分支历史，跨分支合并需要 `merge` / `rebase` 等显式动作
- "worktree 可选"≠"任何等级都可不做 worktree"：见下文默认策略与 Strict Isolation Profile

## 主分支保护

`main` / `master` 只作为稳定集成分支，不直接承载开发提交。实质性编辑前必须先：

1. 运行 `git branch --show-current` 确认当前分支
2. 运行 `git status --short` 确认工作区状态干净
3. 若当前为 `main` / `master`：不得直接落盘，先切到任务分支（L0） 或创建独立 worktree（L1+）
4. 若当前不在主分支：继续在当前任务分支 / worktree 上工作

`main` / `master` 上**不得**存在任何 L1+ 改动；L0 也必须先走任务分支（默认策略见下）。

> **已取代**：早期版本曾允许低风险等级直接在主分支落盘（已过时）。本仓库现行默认：所有等级都先进入任务分支，`main` 仅承载集成。

## 默认策略：分支与 worktree

默认策略按任务等级规定工作方式（与 [task-levels.md](./task-levels.md) 的等级矩阵一一对应）：

| 等级 | 任务分支 | 独立 worktree |
|---|---|---|
| `L0` | **必须**（任务分支） | 可选 |
| `L1` | **必须** | **必须** |
| `L2` | **必须** | **必须** |
| `L3` | **必须** | **必须** |

> **已取代**：早期版本曾以"软推荐 / 分阶段启用"的措辞描述 worktree 强制范围，旧文已从现行规则移除。**现行规则**：L1+ 任何阶段（包括 L2 的 spec / plan 阶段）都必须在独立 worktree 上工作。

## Strict Isolation Profile（接入项目可选声明）

接入本脚手架的项目可以在自己的 `AGENTS.md` Adoption Profile 中显式声明 **Strict Isolation Profile**。声明后：

- **所有等级**（含 `L0`）一律要求独立 worktree；**不得**保留 L0 例外
- L0 仍然只需最小验证，但必须在 worktree 中完成
- 主分支保护进一步收紧：`main` / `master` 不允许任何直接落盘（包括 L0）
- 接入项目不得通过"未声明"的方式偷渡 L0 例外；一旦启用 Strict Isolation，就不允许降级

启用方式：在项目 `AGENTS.md` 的 Adoption Profile 中加一行 `Isolation: strict`（模板字段见 [template/AGENTS.md](../../AGENTS.md)）。未声明则视为默认策略（L0 可选 worktree）。

撤回方式：仅允许通过 ADR / 仓库级变更走流程撤回；不允许在单次任务中临时关闭。

## 分支命名约定

- 默认使用任务分支，分支名格式：`<prefix>-<task-slug>`
- `<prefix>` 按**改动类型**而非 AI 工具（避免分支名锁定到具体 AI 厂商）；采用 conventional commits 风格：

  | 前缀 | 适用改动 |
  |---|---|
  | `feat-` | 新功能、可见行为新增 |
  | `fix-` | 缺陷修复 |
  | `refactor-` | 重构（行为不变） |
  | `chore-` | 仓库级维护（不属以上三类） |
  | `docs-` | 纯文档改动 |
  | `test-` | 仅补测试 |
  | `perf-` | 性能优化 |
  | `build-` | 构建系统 / 依赖调整 |
  | `ci-` | CI 配置调整 |

- `<task-slug>` 使用小写字母、数字和短横线，长度控制在 3-6 个单词
- 同一任务内的多次提交可保留在同一分支，避免无意义的分支膨胀
- 不使用 AI 工具代号作为前缀（如 `codex-` / `claude-` / `cursor-`），原因见上

## worktree 路径与创建

worktree 路径示例：

```text
<仓库根>/.worktrees/<branch-name>/
```

worktree 默认放在仓库根目录下的 `.worktrees/`；只有磁盘空间、权限或特殊调试环境要求时，才放到其他位置，并在任务记录或文档中说明原因。

worktree 与任务分支的区别（一句话）：**任务分支是 `git` 引用；worktree 是物理工作区副本**。任务分支可以"切"；worktree 是"另起一份"。

## 会话起点（多 session 串行）

> **已取代**：本文件早期版本曾以固定 session 数描述多 session 编排（已过时）。session 数与会话职责的权威定义由 [ADR-0003](../adr/0003-multi-session-l2.md) 与对应 runbook 提供；本文件不重复定义。

无论采用何种 session 编排，每个新 session 启动时都必须：

1. **必须**确认当前在哪个任务分支 / worktree 上（`git branch --show-current`）
2. **必须**从仓库文档读取上一 session 的交付物：
   - 设计 / 规划 session 后：`docs/specs/<date>-<name>.md`
   - 计划 session 后：`docs/plans/<date>-<name>.md`
   - 实施 session 后：代码 + spec / plan 末尾的 `## 验证证据` 段
   - 路径命名与元信息规范：[spec-and-plan-naming.md](./spec-and-plan-naming.md)
3. **不允许**依赖会话历史推断上一 session 意图；新 session 没有上一 session 的记忆
4. 评审 session **建议**从新开的 session 开始，避免实施上下文污染

L0 / L1 任务保持单 session；本节约束不向下传递。

## 汇报要求

每次任务汇报中**必须**说明：

- 实际使用的是任务分支还是 worktree（两者并不等价，必须分别说明）
- 是否声明 Strict Isolation Profile
- L2+ 任务当前是哪个 session（具体 session 名以 runbook / ADR-0003 为准）
- 列出执行过的验证命令
- 列出未执行的验证及其原因
- L3 任务的"已批准"信号来源（issue / 评论 / 显式消息）

## 关联

- 任务分级：[task-levels.md](./task-levels.md)
- 治理基线：[governance-core.md](./governance-core.md)
- 接入模板：[../../template/AGENTS.md](../../AGENTS.md)
- ADR：[../adr/0003-multi-session-l2.md](../adr/0003-multi-session-l2.md)、[../adr/0005-l3-approval-gate.md](../adr/0005-l3-approval-gate.md)