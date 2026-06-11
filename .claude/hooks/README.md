# Claude Code Hooks（占位）

本目录为可选的 Claude Code hooks 配置。

## 状态

**当前未配置任何 hook**——本脚手架本身不绑定强制 hook，原因是：

- 不同项目有不同的"完成"语义，hook 的硬阻塞可能与项目需要不符
- 仓库级治理规则已在 `AGENTS.md` 与 `docs/ai/` 充分描述，hook 是"加固"而非"主约束"
- 跨 AI 工具兼容性：hook 是 Claude Code 特有，其他 AI 工具（Curso / Aider / Copilot）不支持

## 推荐的占位 hook 示例

如果项目需要强化约束，可在 `.claude/settings.json` 的 `hooks` 字段中启用：

### PreToolUse：提交前检查 L2+ 是否已写 spec/plan

在 `git commit` 前检查工作区是否有未提交的 `docs/specs/` 或 `docs/plans/` 文档，作为对 L2 准入的软提醒。

### PostToolUse：写文件后提醒运行验证

在 `Write` / `Edit` 工具调用完成后，提示 AI 检查是否需要运行项目验证基线。

### Stop：会话结束前检查汇报完整性

在会话结束事件触发时，检查 AI 是否在最终汇报中列出了：变更级别、验证命令、验证结果、未跑项及原因。

## 端口到其他 AI 工具

| 工具 | 等价机制 |
|---|---|
| Cursor | `.cursorrules` 或仓库根的 `AGENTS.md`（已支持） |
| Aider | `CONVENTIONS.md` 或仓库根的 `AGENTS.md`（已支持） |
| GitHub Copilot | 仓库根 `AGENTS.md`（已支持） |
| Cody | `.cody/config.json` |
| Continue | `.continue/config.json` |
| 其他 | 参考各工具的"项目级指令"机制 |

本仓库的核心约束不依赖任何工具的 hook 能力，**所有 AI 工具都能通过 `AGENTS.md` 入口** 理解本仓库的治理规则。

详见各 AI 工具的官方文档。
