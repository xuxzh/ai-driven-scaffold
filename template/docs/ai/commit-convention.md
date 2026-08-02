# Commit Convention

> **这是单点定义文件**。所有 git 提交信息、PR/MR 描述的格式、AI 提交边界与硬约束都按此文件。Summary 仅提供快速入口（见 [commit-convention-summary.md](./commit-convention-summary.md)）；具体 type 语义、scope 规则、breaking change 标记与 AI 行为约束以本文为权威。

## 目的

建立人工与 AI 共享的提交边界、硬约束与证据规则：

- 让 `git log` 与 `git blame` 能直接回答"这次改动是什么 / 为什么 / 影响谁"
- 让 PR/MR 描述自带最小可读字段，减少评审者追问
- 让 AI 不擅自扩大提交边界（不得"顺手提交无关修改"）
- 让 verify 证据、spec/plan 引用、issue 关闭路径在提交与合并时一并可见

## Conventional Commit 基础格式

标准格式：

```text
<type>(<scope>): <subject>

<body>

<footer>
```

- `<type>` **必填**，必须落在 11 类白名单（见下）
- `(<scope>)` **可选**——不写 scope 也接受；写 scope 时需用名词短语、保持小写、不带空格
- `<subject>` **必填**——用一句话说明"做了什么"；中文 / 英文均可；结尾不写句号；祈使语气（"新增" / "add"，不写"新增了" / "added"）
- `<body>` 可选——多段落说明"为什么这样做" / "与之前的差异"；与 `<subject>` 之间留一个空行
- `<footer>` 可选——多个段落时使用 token 标记（`BREAKING CHANGE:` / `Refs:` / `Closes:` 等）

## Type 白名单（11 类）

| Type | 含义 | 典型场景 |
|---|---|---|
| `feat` | 新功能 / 可见行为新增 | 新增 API、新增用户可见功能、新增配置项 |
| `fix` | 缺陷修复 | 修复用户可见的 bug、修复行为回退、修复错别字影响行为的部分 |
| `docs` | 纯文档改动 | `docs/` 目录、`AGENTS.md`、README、注释（JSDoc / docstring 等纯文档） |
| `style` | 不影响语义的格式变更 | 空白 / 缩进 / 引号 / 换行 / 格式化工具产物 |
| `refactor` | 重构（行为不变） | 提取函数、改名、内部结构调整、消除重复 |
| `perf` | 性能优化 | 算法 / 数据结构 / 资源占用的可见改进 |
| `test` | 仅补测试 | 新增测试用例、补齐断言、修复测试夹具 |
| `build` | 构建系统 / 依赖调整 | 打包工具、依赖版本、构建脚本、产物路径 |
| `ci` | CI 配置调整 | GitHub Actions / GitLab CI / pre-commit 等流水线配置 |
| `chore` | 仓库级维护 | 不属于以上三类的元维护（如 .gitignore / 编辑器配置） |
| `revert` | 撤销先前的提交 | 引用被撤销 commit 的 SHA，并说明原因 |

**不接受的 type**：`feat!` / `feature` / `bug` / `hotfix` / `wip` / `misc` 等自定义或别名。

## Scope 可选规则

- 默认**可选**——单文件内提交、不涉及模块边界时可省略 scope
- 写 scope 时**必须**遵守：
  - 使用小写英文或与目录同名的中文术语
  - 不带空格 / 不带特殊字符；多词用短横线连接（如 `session-handoff` / `commit-convention`）
  - 指明受影响模块 / 目录 / 层次（如 `docs/ai` / `scripts` / `ci` / `runtime`）
- 跨多个不相关模块的提交 → 优先**拆成多个 commit**（见下"提交边界"），而不是写一个泛 scope（如 `misc` / `everything`）
- 同一分支内多次提交的 scope 应保持语义一致；频繁切换 scope 视为"边界模糊"，评审者会要求拆分

## 描述格式

- 中文 / 英文均可，但**必须**与仓库已有提交语言保持一致；混用时需在 `<body>` 中说明
- `<subject>` 长度建议 ≤ 72 字符（含 type / scope / 冒号 / 空格）；超过时把细节下沉到 `<body>`
- `<body>` 段落首行不缩进，行宽建议 72–100 字符
- `<body>` 中按"动机 / 改动点 / 影响面"组织；不要堆砌实现细节

## Breaking Change 标记

两种方式任选其一，可叠加使用：

1. **感叹号**（在 type / scope 之后）：

   ```text
   feat(api)!: 重命名 userId → user_id
   ```

2. **footer 标记**（在 commit body 之后）：

   ```text
   BREAKING CHANGE: userId 字段统一改名为 user_id，迁移脚本见 docs/migration/2026-08-user-id.md
   ```

- 单一提交同时有两种标记时，**两处必须一致**；不一致视为评审退回项
- Breaking change 必须在 PR/MR 描述的"风险 / 回滚"段显式列出影响面、回滚路径、迁移步骤

## Footer 字段

可包含以下 token（与 `<body>` 之间留一个空行）：

| Token | 含义 | 示例 |
|---|---|---|
| `BREAKING CHANGE:` | 标记破坏性变更 | `BREAKING CHANGE: <说明>` |
| `Closes:` | 关闭 issue（合并后自动关闭） | `Closes: #123` |
| `Refs:` | 引用 issue / spec / plan / ADR | `Refs: docs/specs/2026-08-01-xxx.md, #456` |
| `Reviewed-by:` | 评审者（人工填） | `Reviewed-by: <name>` |
| `Tested-by:` | 验证者 | `Tested-by: <name>` |

- `Closes:` / `Refs:` 必须使用仓库可解析的链接（GitHub issue 号 / spec / plan / ADR 路径）
- 多个 `Refs:` 之间用逗号或换行分隔

## 提交边界（推荐切片）

推荐按以下切片分提交，避免"一次提交混合多类改动"：

| 切片 | 何时单独提交 | 备注 |
|---|---|---|
| `spec` | L2+ 任务的 spec 落字（`docs/specs/<date>-<name>.md`） | 不与代码改动混合 |
| `plan` | L2+ 任务的 plan 落字（`docs/plans/<date>-<name>.md`） | 不与代码改动混合 |
| `implementation` | 主体代码改动 | 一次提交对应一个可独立验证的切片 |
| `review follow-up` | 评审要求的修复 / 调整 | 引用评审报告路径 |
| `docs` / `chore` | 文档 / 元维护 | 不与代码改动混合 |

**反例（禁止）**：

- 不得为了"提交整齐"把无关修改混入同一提交（如把 typo 修复与功能改动塞进同一 commit）
- 不得把多模块的独立变更塞进同一 commit 仅为减少 commit 数量
- 不得把 verify 失败的临时调试代码与已通过的代码放在同一 commit

## AI 行为约束（硬约束）

以下约束是 AI 提交行为的硬边界；缺任一条约束对应的明确授权，AI **不得**继续：

1. **默认不自动 commit**：除非用户在本轮对话中**明确要求**"提交" / "commit" / "commit 一下" / "push 上去" / "提交并推送"，AI 不得跑 `git commit` / `git push` / `git tag` / 任何写历史的命令
2. **不得跳过 hooks**：除非用户**明确要求** `--no-verify` / "跳过 hooks"，AI 不得使用 `--no-verify`；pre-commit / commit-msg / pre-push 失败时必须先解决根因，不允许"先绕过去再说"
3. **不得 amend 未授权提交**：除非用户**明确要求** `git commit --amend` / "amend 一下"，AI 不得修改已存在的提交；amend 仅作用于"上一次提交"且修改内容必须与原提交语义一致
4. **不得 force-push**：除非用户**明确要求** `--force-with-lease` / "强推"，AI 不得跑 `git push --force` / `git push -f`；提交到共享分支的 force-push 需用户二次确认
5. **不得擅自构造提交者身份**：不得通过 `git config` 临时改 `user.name` / `user.email` / `GIT_AUTHOR_*` 绕过提交归属检查；如需代签，需用户明确说明并保留可审计痕迹

## PR / MR 描述最小字段

PR/MR 描述（GitHub PR body / GitLab MR description）**至少**包含以下字段：

| 字段 | 必填 | 内容要求 |
|---|---|---|
| 目标（Goal） | 必填 | 一句话说明本次合并要达成的结果 |
| 范围（Scope） | 必填 | 列出涉及的文件 / 模块 / 行为变化 |
| 非目标（Non-goals） | 必填 | 显式声明本次不做的改动 |
| 验证证据（Verification） | 必填 | 命令清单、退出码、关键输出摘要（继承 [ADR-0002](./../adr/0002-verify-hard-gate.md)） |
| 风险 / 回滚（Risk / Rollback） | 必填 | 主要风险点、回滚路径、回滚命令 |
| 关联 spec / plan | L2+ 必填 | `Refs:` 到 `docs/specs/<date>-<name>.md` + `docs/plans/<date>-<name>.md` |
| 关联 issue | 关联时必填 | `Closes:` / `Refs:` 到 issue 编号或链接 |

L2+ 任务的 PR/MR 描述与 spec / plan 双份末尾的 `## 验证证据` 段必须互相引用——评审者按 [review-checklist.md](./checklists/review-checklist.md) 同时核对 PR 描述与仓库文档。

## 完整示例

```text
feat(docs/ai): 新增 commit convention 单点规范

- 定义 11 类 Conventional Commit type 白名单
- 明确 AI 默认不自动 commit、不得跳过 hooks、不得 amend 未授权提交
- 定义推荐提交边界（spec / plan / implementation / review follow-up 分提交）

Refs: docs/plans/2026-08-01-ai-session-batch-and-dogfood.md
```

## 反模式（不应出现的写法）

- 提交信息只有 `<type>: ` 加空 subject，或 subject 是 "update" / "fix bug" / "WIP" / "tmp"
- 提交信息使用 emoji / 装饰字符作为 type 前缀（如 `:sparkles: feat:`）
- 一次提交跨越 ≥ 3 个不相关模块
- 一次提交混合代码改动、格式修复、调试代码回退
- 把未通过 verify 的代码与已通过的代码合在同一 commit
- amend / force-push 未取得用户明确授权
- PR/MR 描述只写"修复了几个 bug"，无验证证据与回滚路径

## 关联

- 提交边界摘要：[commit-convention-summary.md](./commit-convention-summary.md)
- AI 角色边界：[ai-role-boundaries.md](./ai-role-boundaries.md)
- 任务分级：[task-levels.md](./task-levels.md)
- 完成定义：[completion-criteria.md](./completion-criteria.md)
- 验证基线：[verification-baseline.md](./verification-baseline.md)
- 评审清单：[checklists/review-checklist.md](./checklists/review-checklist.md)
- 分支与 worktree：[branch-strategy.md](./branch-strategy.md)
- ADR：[../adr/0002-verify-hard-gate.md](../adr/0002-verify-hard-gate.md) / [../adr/0003-multi-session-l2.md](../adr/0003-multi-session-l2.md) / [../adr/0004-l2-spec-and-plan.md](../adr/0004-l2-spec-and-plan.md) / [../adr/0005-l3-approval-gate.md](../adr/0005-l3-approval-gate.md)