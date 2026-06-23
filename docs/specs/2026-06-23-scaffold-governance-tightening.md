# Scaffold Governance Tightening 设计

## 背景

本脚手架的定位是语言无关、工具无关的 AI 驱动开发治理包。当前治理主线已经清晰：`AGENTS.md` 作为统一入口，`docs/ai/` 承载单点定义、模板、runbook 和 checklist，`docs/adr/` 承载长期决策。

本次架构审视暴露出 6 个需要收敛的结构问题：

- 项目元信息与接入状态散落在 `AGENTS.md`、`docs/ai/context-index.md` 和 `scripts/scaffold-doctor.sh`，缺少一个稳定的 adoption profile 概念。
- `AGENTS.md`、`context-index.md`、runbook 与 checklist 中存在规则复述，和 `CONTRIBUTING.md` 的单点化原则存在张力。
- `docs/ai/context-index.md` 仍保留 L2 “spec 或 plan”的旧表述，和 ADR-0004 后的 “spec 和 plan 双份”不一致。
- ADR-0002 / 0003 / 0004 / 0005 仍为 `Proposed`，但 `AGENTS.md` 已把它们作为硬约束依据。
- `.claude/` 提供 Claude 专属配置与 hook 占位，会让脚手架显得绑定 Claude；其中 `settings.json` 又允许 `git add` / `git commit`，和 L3 未批准不得执行这些动作的规则形成表面冲突。
- `scaffold-doctor.sh` 无法区分“模板仓库保留占位符”与“目标项目接入未完成”，导致当前模板仓库自检出现预期失败但语义不够清楚。

## 目标

把脚手架治理调整为更明确的“工具无关治理核心 + 可选接入检查”结构，降低规则漂移、工具绑定和接入误读。

## 非目标

- 不引入 Node / Python / Rust / Go 等运行时依赖。
- 不把 doctor 升级为完整 CLI 或自动修复工具。
- 不新增 Claude、Cursor、Aider、Copilot 等任何工具专属配置。
- 不改变 L0/L1/L2/L3 的核心风险分级含义。
- 不改变 L3 “无批准不得 `git add` / `git commit` / patch / push”的规则本身。
- 不把本次调整扩展为完整 issue 流转、PR 模板或 CODEOWNERS 门禁。

## 范围级别

- 建议任务级别：`L3`
- 理由：本次调整触及仓库级治理入口、ADR 状态、工具兼容性、隐藏配置目录删除、脚本行为和接入文档语义，属于全局脚手架约定调整。

## 受影响边界

- 仓库入口：`AGENTS.md`
- 上下文导航：`docs/ai/context-index.md`
- 治理单点和 runbook：按最小必要范围修正重复或旧表述
- ADR：`docs/adr/0002-verify-hard-gate.md`、`0003`、`0004`、`0005`
- 工具专属配置：删除 `.claude/`
- 接入检查：`scripts/scaffold-doctor.sh` 与 `docs/ai/checklists/adoption-checklist.md`
- README / CONTRIBUTING：同步删除 Claude 专属配置说明，改为工具无关说明

## 建议方案

采用一个 L3 umbrella 调整，分 6 个可验证切片推进：

1. 删除 `.claude/`，把 README / CONTRIBUTING 中的 Claude 专属配置表述改成工具无关说明。
2. 修正 L2 相关旧表述，尤其是 `context-index.md` 中 “spec 或 plan”。
3. 将 ADR-0002 / 0003 / 0004 / 0005 状态调整为与硬约束使用方式一致的 `Accepted`。
4. 引入最小的 adoption profile 概念：不新增复杂配置文件，先在文档中命名“项目元信息 + 接入状态”的单一概念，并让 doctor 输出围绕它解释。
5. 调整 doctor，增加模板仓库与已接入项目两种模式，避免模板状态被误读为接入失败。
6. 跑文档自检、doctor 两种模式和 shell 语法检查，把验证证据写回 plan。

## 备选方案

### 方案 A：保留 `.claude/`，补 hook 示例

优点是对 Claude Code 用户更直接。缺点是与脚手架“跨 AI 工具兼容”的定位不一致，而且 hook 仍然不是通用能力。拒绝理由：本次目标是去工具绑定，而不是强化某个工具的适配层。

### 方案 B：新增 `.scaffold-profile.yml`

优点是 adoption profile 可以真正结构化，doctor 读取更简单。缺点是引入新配置文件后，用户需要维护 AGENTS 元信息和 profile 双份，反而增加接入负担。拒绝理由：第一步先做概念和脚本语义收敛，不新增配置源。

### 方案 C：把 doctor 改成强制门禁

优点是执行更硬。缺点是当前 doctor 只检查接入状态，不证明业务 verify；强行门禁会扩大它的职责。拒绝理由：doctor 仍保持只读接入检查，不替代项目 `verify`。

## L3 批准要求

实施 session 启动前必须收到用户明确批准信号，且批准信号必须引用本 spec 或配套 plan 路径。

批准范围仅限本文档和配套 plan 中列出的文件与行为。实施中若发现需要新增配置文件、改动 CI 行为、引入依赖或改变 L0/L1/L2/L3 规则含义，必须停止并重新请求批准。

## 验证计划

- `bash -n scripts/scaffold-doctor.sh`
- `bash scripts/scaffold-doctor.sh --template`
- `bash scripts/scaffold-doctor.sh --adopted`
- 扫描 `.claude` 引用是否只剩历史说明或完全清除。
- 扫描 `spec 或 plan` / `正式 spec 或 plan` 是否不再出现在 L2 准入语境。
- 扫描 ADR-0002 / 0003 / 0004 / 0005 状态是否不再为 `Proposed`。
- 扫描 Markdown 中 `<...>` 占位符是否仍处于模板或检查目标语境。

## 风险

- 删除 `.claude/` 后，Claude Code 用户少一个即开即用示例；通过 README 的工具无关说明缓解。
- doctor 增加模式后，用户可能不知道选哪一个；通过默认行为和 adoption checklist 说明缓解。
- ADR 状态改为 `Accepted` 会让硬约束语义更强；这与当前 `AGENTS.md` 的用法一致，但需要确保没有残留 “Proposed” 叙述。
- adoption profile 只做概念收敛，不新增结构化配置，短期仍依赖 `AGENTS.md` 表格作为实际填写位置。

## 需要更新的文档

- `README.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- `docs/ai/context-index.md`
- `docs/ai/checklists/adoption-checklist.md`
- `docs/adr/0002-verify-hard-gate.md`
- `docs/adr/0003-multi-session-l2.md`
- `docs/adr/0004-l2-spec-and-plan.md`
- `docs/adr/0005-l3-approval-gate.md`
- `docs/adr/README.md`（如需要标注状态语义）

## 批准（L3 任务必填）

- 批准时间：2026-06-23
- 批准来源：用户会话消息：“已批准实施 /Users/xuxz/repos/ruihui/.worktrees/ai-driven-scaffold/chore-scaffold-governance-tightening/docs/specs/2026-06-23-scaffold-governance-tightening.md 和 /Users/xuxz/repos/ruihui/.worktrees/ai-driven-scaffold/chore-scaffold-governance-tightening/docs/plans/2026-06-23-scaffold-governance-tightening.md”
- 批准范围：本 spec 与配套 plan 中显式声明的范围

## 验证证据（实施 session 末尾必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |

未跑项：
