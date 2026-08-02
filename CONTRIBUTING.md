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
- 流程：先在 `template/docs/adr/` 新增 ADR 解释新增/删除的理由
- 验证：跑一次 [review-checklist.md](template/docs/ai/checklists/review-checklist.md) 自查

### CI 模板调整、跨工具兼容性变更

- 等级：`L2`
- 流程：先写 spec / plan；保持语言无关原则

### 引入示例代码 / 引入具体技术栈绑定

- 等级：`L3`
- 流程：先在 `template/docs/adr/` 写 ADR 解释为什么需要打破"语言无关"承诺
- 必须人工主导

### 引入 AI 工具专属配置

- 等级：`L3`
- 流程：先写 spec / plan，并在 `template/docs/adr/` 解释为什么需要打破"工具无关"承诺
- 必须人工主导
- 默认不在脚手架中维护 Claude / Cursor / Aider / Copilot 等任一工具的专属配置；项目可自行添加可选加固层

## 单点化原则

本脚手架的治理规则**单点化**：

- 任务分级只在 [task-levels.md](template/docs/ai/task-levels.md) 定义
- 完成定义只在 [completion-criteria.md](template/docs/ai/completion-criteria.md) 定义
- 验证基线只在 [verification-baseline.md](template/docs/ai/verification-baseline.md) 定义
- 分支策略只在 [branch-strategy.md](template/docs/ai/branch-strategy.md) 定义
- AI 边界只在 [ai-role-boundaries.md](template/docs/ai/ai-role-boundaries.md) 定义
- 回写规则只在 [doc-rewriting-rules.md](template/docs/ai/doc-rewriting-rules.md) 定义

**禁止在其他文档中复述这些规则**。如需引用，用相对链接指向单点文件。

`template/scripts/scaffold-doctor.sh` 只能做只读检查，不得自动修改用户项目文件或引入具体语言运行时依赖。

## 新增单点定义时的检查清单

1. 是否真的需要新单点？（能否合并到已有单点？）
2. 是否在多个文件中有重复定义？（如有，先删除重复，再创建单点）
3. 单点的命名是否清晰？（避免歧义、避免与已有单点冲突）
4. 是否更新了 `template/docs/ai/governance-core.md` 的索引？
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
- 默认 AI 工具为 Claude / Cursor / Aider / Copilot

## 验证清单（修改后自检）

> **与 CI 同口径**：下面这一组命令与 [template/.github/workflows/ci.yml](template/.github/workflows/ci.yml) / [template/.gitlab-ci.yml](template/.gitlab-ci.yml) 的 5 个 job 等价。本地跑通后即可声称"已自检通过"，无需再额外跑 CI。

```bash
# lint-shell —— bash 语法校验（不执行）
bash -n template/scripts/scaffold-doctor.sh
bash -n template/scripts/worktree-add.sh
bash -n template/scripts/hooks/rewrite-worktree-add.sh

# lint-python —— Python 检查器与单测
python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v

# check-links —— Markdown 相对链接检查（template 模式）
python3 template/scripts/check-markdown-links.py --root . --template

# check-governance —— 治理规则一致性（GOV001-GOV004）
python3 template/scripts/check-governance-consistency.py --root . --template

# check-doctor —— 聚合自检 + 集成测试
bash template/scripts/scaffold-doctor.sh --template
bash template/scripts/tests/scaffold-doctor-test.sh
bash template/scripts/tests/worktree-add-test.sh
```

本仓库属于**脚手架自身**，跑 `--template` 模式；接入本脚手架的目标项目跑默认 `bash template/scripts/scaffold-doctor.sh`（等价 `--adopted`）。

补充检查项（CI 未覆盖、但维护者建议跑一遍）：

- [ ] 跑 `grep -rE 'pnpm|react|vue|svelte|tailwind|vitest|jest|axios' --include='*.md' --exclude=AGENTS.md .`（应只在"示例"语境中命中；`AGENTS.md` 的 Adoption Profile 是本仓库事实陈述，非默认推荐；`template/AGENTS.md` 仍被检查，因其只含 `<...>` 占位符）
- [ ] 检查所有相对链接可达：`grep -oE '\]\([^)]+\.md\)' AGENTS.md template/docs/ai/*.md`
- [ ] 检查目录树：`find . -type d | sort`
- [ ] 跑 `git diff --check`，确认无尾随空格 / 冲突标记
- [ ] 跑 YAML 语法校验：`template/.gitlab-ci.yml` 和 `template/.github/workflows/ci.yml`（`python3 -c "import yaml; yaml.safe_load(open('template/.gitlab-ci.yml'))"`；GitHub Actions YAML 由 CI 自身校验）

## 提交信息规范

- `docs(ai): <变更>` —— 修改 `template/docs/ai/` 内文档
- `docs(adr): <变更>` —— 新增或修改 ADR
- `feat(scaffold): <变更>` —— 新增功能（如新增模板）
- `fix(scaffold): <变更>` —— 修复链接、占位符、YAML 语法等
- `chore(scaffold): <变更>` —— 杂项维护

## 许可

提交即表示同意以 MIT 许可证贡献。
