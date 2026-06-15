# 贡献指南

本脚手架本身是一个**使用本治理的项目**——任何对脚手架的修改都应该按它自己定义的规则进行。

## 修改类型与对应流程

### 纯文档修改（拼写、措辞、链接修复）

- 等级：`L0`
- 流程：直接修改并 commit
- 验证：跑一次文档自检（grep 确认无 Web/TS 特定内容残留）

### 单点定义调整（task-levels 等）

- 等级：`L1`
- 流程：先在 PR 描述中说明影响范围（哪些文件需要同步更新引用）
- 验证：检查所有引用该单点的文件，链接仍然可达、措辞不再漂移

### 新增单点定义 / 删除单点定义

- 等级：`L2`
- 流程：先在 `docs/adr/` 新增 ADR 解释新增/删除的理由
- 验证：跑一次 [review-checklist.md](docs/ai/checklists/review-checklist.md) 自查

### CI 模板调整、跨工具兼容性变更

- 等级：`L2`
- 流程：先写 spec / plan；保持语言无关原则

### 引入示例代码 / 引入具体技术栈绑定

- 等级：`L3`
- 流程：先在 `docs/adr/` 写 ADR 解释为什么需要打破"语言无关"承诺
- 必须人工主导

## 单点化原则

本脚手架的治理规则**单点化**：

- 任务分级只在 [task-levels.md](docs/ai/task-levels.md) 定义
- 完成定义只在 [completion-criteria.md](docs/ai/completion-criteria.md) 定义
- 验证基线只在 [verification-baseline.md](docs/ai/verification-baseline.md) 定义
- 分支策略只在 [branch-strategy.md](docs/ai/branch-strategy.md) 定义
- AI 边界只在 [ai-role-boundaries.md](docs/ai/ai-role-boundaries.md) 定义
- 回写规则只在 [doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md) 定义

**禁止在其他文档中复述这些规则**。如需引用，用相对链接指向单点文件。

## 新增单点定义时的检查清单

1. 是否真的需要新单点？（能否合并到已有单点？）
2. 是否在多个文件中有重复定义？（如有，先删除重复，再创建单点）
3. 单点的命名是否清晰？（避免歧义、避免与已有单点冲突）
4. 是否更新了 `docs/ai/governance-core.md` 的索引？
5. 是否更新了 `AGENTS.md` 的入口链接？

## 语言无关原则的边界

允许出现的内容：

- 列举多种包管理器作为示例：`pnpm / npm / yarn / uv / cargo / go / mix`
- 列举多种查询库作为示例：`TanStack Query / SWR / Riverpod / reactive`
- 列举多种 AI 工具作为示例：`Claude Code / Cursor / Aider / Copilot`

不允许出现的内容：

- 默认包管理器为 `pnpm`
- 默认查询库为 `TanStack Query`
- 默认框架为 React / Vue / Svelte
- 默认测试框架为 Vitest / Jest
- 默认 i18n 库为 i18next
- 默认 HTTP 客户端为 fetch / axios
- 默认 CI 为 GitLab CI（应同时提供 GitHub Actions）

## 验证清单（修改后自检）

- [ ] 跑 `grep -rE 'pnpm|react|vue|svelte|tailwind|vitest|jest|axios' --include='*.md' .`（应只在"示例"语境中命中）
- [ ] 检查所有相对链接可达：`grep -oE '\]\([^)]+\.md\)' AGENTS.md docs/ai/*.md`
- [ ] 检查目录树：`find . -type d | sort`
- [ ] 跑 YAML 语法校验：`.gitlab-ci.yml` 和 `.github/workflows/ci.yml`

## 提交信息规范

- `docs(ai): <变更>` —— 修改 `docs/ai/` 内文档
- `docs(adr): <变更>` —— 新增或修改 ADR
- `feat(scaffold): <变更>` —— 新增功能（如新增模板）
- `fix(scaffold): <变更>` —— 修复链接、占位符、YAML 语法等
- `chore(scaffold): <变更>` —— 杂项维护

## 许可

提交即表示同意以 MIT 许可证贡献。
