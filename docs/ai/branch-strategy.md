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

## 汇报要求

每次任务汇报中**必须**说明：

- 实际使用的是任务分支还是 worktree
- 列出执行过的验证命令
- 列出未执行的验证及其原因

## 关联

- 任务分级：[task-levels.md](./task-levels.md)
- 治理基线：[governance-core.md](./governance-core.md)
