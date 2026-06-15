# 分支与 worktree 策略

> **这是单点定义文件**。所有改动前的分支检查、worktree 选择、命名约定都按此文件。

## 主分支保护

`main` / `master` 只作为稳定集成分支，不直接承载开发提交。实质性编辑前必须先：

1. 运行 `git branch --show-current` 确认当前分支
2. 运行 `git status --short` 确认工作区状态干净
3. 不在主分支时：继续在当前任务分支上工作
4. 在主分支时：先切到任务分支或创建隔离 worktree

## 分支命名约定

- 默认使用任务分支，分支名格式：`<prefix>-<task-slug>`
- `<prefix>` 推荐使用 AI 工具代号（便于区分 AI 协助创建的分支），例如：
  - `codex-<task-slug>`（默认建议）
  - `claude-<task-slug>`
  - `cursor-<task-slug>`
- `<task-slug>` 使用小写字母、数字和短横线，长度控制在 3-6 个单词
- 同一任务内的多次提交可保留在同一分支，避免无意义的分支膨胀

## worktree 使用约定

| 任务级别 | 默认工作方式 |
|---|---|
| `L0` / `L1` | 独立任务分支，不需要 worktree |
| `L2` / `L3` | 仓库级 worktree，路径为仓库根目录下的 `.worktrees/` |

worktree 路径示例：

```text
<仓库根>/.worktrees/<branch-name>/
```

worktree 默认放在仓库根目录下的 `.worktrees/`；只有磁盘空间、权限或特殊调试环境要求时，才放到其他位置，并在任务记录或文档中说明原因。

worktree 与任务分支的区别：

- 任务分支：直接在工作区切换，适合短平快的 L0/L1 改动
- worktree：独立的工作区副本，适合需要并行任务、长时间独占或 L2/L3 重构

## 会话起点（多 session 串行）

L2+ 任务按"设计 / 计划 / 实施 / 评审" 4 个 session 串行（详见 [ADR-0003](../adr/0003-multi-session-l2.md)）。每个新 session 启动时：

1. **必须**确认当前在哪个任务分支 / worktree 上（`git branch --show-current`）
2. **必须**从仓库文档读取上一 session 的交付物：
   - 设计 session 后：`docs/specs/<date>-<name>.md`
   - 计划 session 后：`docs/plans/<date>-<name>.md`
   - 实施 session 后：代码 + spec / plan 末尾的 `## 验证证据` 段
3. **不允许**依赖会话历史推断上一 session 意图；新 session 没有上一 session 的记忆
4. 评审 session **建议**从新开的 session 开始，避免实施上下文污染

L0 / L1 任务保持单 session；本节约束不向下传递。

## 汇报要求

每次任务汇报中**必须**说明：

- 实际使用的是任务分支还是 worktree
- L2+ 任务当前是哪个 session（设计 / 计划 / 实施 / 评审）
- 列出执行过的验证命令
- 列出未执行的验证及其原因
- L3 任务的"已批准"信号来源（issue / 评论 / 显式消息）

## 关联

- 任务分级：[task-levels.md](./task-levels.md)
- 治理基线：[governance-core.md](./governance-core.md)
- ADR：[../adr/0003-multi-session-l2.md](../adr/0003-multi-session-l2.md)、[../adr/0005-l3-approval-gate.md](../adr/0005-l3-approval-gate.md)
