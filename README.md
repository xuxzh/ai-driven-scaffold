# AI-Driven Scaffold

> **语言无关的 AI 驱动开发治理脚手架**——把"文档驱动、验证优先、AI 受控执行"的研发治理抽离为可复用的模板仓库。

## 适用对象

- 想在自己的项目中接入 AI 协作流程的个人或小团队开发者
- 已经用 AI 写代码，但缺少任务分级、验证基线、文档回写等约束的项目
- 任何语言/框架的项目——本脚手架不绑定具体技术栈

## 不适用

- 已经在用类似治理（CLAUDE.md、Cursor rules、GitHub spec-kit）并满意的项目
- 追求 AI 全面自治编码的实验性项目
- 没有文档维护习惯的短期一次性项目

## 5 分钟上手

### 方式 1：用 GitHub 模板创建新仓库

```bash
gh repo create my-project --template https://github.com/xuxzh/ai-driven-scaffold --private --clone
cd my-project
```

### 方式 2：手动克隆并裁剪

```bash
git clone https://github.com/xuxzh/ai-driven-scaffold my-project
cd my-project
rm -rf .git
git init -b main
```

### 方式 3：把治理层注入既有项目

```bash
# 假设你的项目根目录在 ~/my-existing-project
cd ~/my-existing-project

# 0. 临时克隆模板到 /tmp（不污染你的项目）
git clone https://github.com/xuxzh/ai-driven-scaffold /tmp/ai-scaffold

# 1. 复制治理文档
cp -r /tmp/ai-scaffold/docs/ai docs/
cp -r /tmp/ai-scaffold/docs/adr docs/
cp /tmp/ai-scaffold/AGENTS.md AGENTS.md

# 2. 如果项目还没有 docs/specs/ 和 docs/plans/，创建它们
mkdir -p docs/specs docs/plans
touch docs/specs/.gitkeep docs/plans/.gitkeep

# 3. 编辑 AGENTS.md 顶部的"用户项目元信息"段落
#    把 5 个占位符（<pm> / <app-dir> / <entry-file> / <shared-dir> / <test-dir>）
#    替换为你的项目实际值

# 4. 清理临时克隆
rm -rf /tmp/ai-scaffold
```

> **注意**：`cp -r docs/ai docs/` 要求 `docs/` 目录已存在；如不存在，先 `mkdir -p docs/` 再复制。

## 接入后的 4 步

1. **补全项目元信息**——编辑 `AGENTS.md` 顶部的"用户项目元信息"，填入包管理器、命令、入口等
2. **必须定义 `verify` 命令**——在你项目的 manifest 中定义一个 `verify` 入口，串联 lint → typecheck → test → build；L1+ 任务完成前 AI 必跑（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）
3. **跑一次 L0 任务试水**——用本文档试一次小改动，跑一次最小验证
4. **跑一次 L2 任务验证流程**——按 [l2-multi-session-runbook.md](docs/ai/runbooks/l2-multi-session-runbook.md) + [feature-delivery-runbook.md](docs/ai/runbooks/feature-delivery-runbook.md) 跑通一次新功能（4 session 串行：设计 → 计划 → 实施 → 评审）

## 核心治理机制

- **任务分级 L0/L1/L2/L3**：见 [docs/ai/task-levels.md](docs/ai/task-levels.md)
  - `L0` 单文件 + 不跨模块的轻量改动，直接做 + 最小验证
  - `L1` 2-4 文件的常规改动，task packet 先行
  - `L2` 跨文件 / 数据流 / 入口流转，spec **和** plan 双份都需提交，强制多 session 串行
  - `L3` 高风险改动，人工主导 + spec/plan + **Pre-Implementation Approval Gate**
- **完成定义 5 条件**：见 [docs/ai/completion-criteria.md](docs/ai/completion-criteria.md)
- **验证基线分层**：见 [docs/ai/verification-baseline.md](docs/ai/verification-baseline.md)（L1+ AI 必跑 verify）
- **分支与 worktree 策略**：见 [docs/ai/branch-strategy.md](docs/ai/branch-strategy.md)
- **AI 角色边界**：见 [docs/ai/ai-role-boundaries.md](docs/ai/ai-role-boundaries.md)（L2+ 角色边界=会话边界）
- **文档回写规则**：见 [docs/ai/doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md)
- **仓库术语表**：[docs/CONTEXT.md](docs/CONTEXT.md)
- **硬约束 ADR**：
  - [ADR-0002 verify 硬门禁](docs/adr/0002-verify-hard-gate.md)
  - [ADR-0003 L2+ 多 session](docs/adr/0003-multi-session-l2.md)
  - [ADR-0004 L2 spec + plan](docs/adr/0004-l2-spec-and-plan.md)
  - [ADR-0005 L3 审批门禁](docs/adr/0005-l3-approval-gate.md)

## 模板与清单

- 任务包（L1）：[docs/ai/templates/task-packet.md](docs/ai/templates/task-packet.md)
- 功能设计（L2 spec）：[docs/ai/templates/feature-spec.md](docs/ai/templates/feature-spec.md)
- 实施计划（L2 plan）：[docs/ai/templates/implementation-plan.md](docs/ai/templates/implementation-plan.md)
- 缺陷修复：[docs/ai/templates/bugfix-brief.md](docs/ai/templates/bugfix-brief.md)
- 重构：[docs/ai/templates/refactor-brief.md](docs/ai/templates/refactor-brief.md)
- 评审清单：[docs/ai/checklists/review-checklist.md](docs/ai/checklists/review-checklist.md)
- ADR 模板：[docs/adr/adr-template.md](docs/adr/adr-template.md)

## 跨 AI 工具兼容

本脚手架的核心约束通过 `AGENTS.md` 入口表达，被以下 AI 工具自动识别：

- **Claude Code**：直接读取 `AGENTS.md`
- **Cursor**：读取 `AGENTS.md` 或 `.cursorrules`
- **Aider**：读取 `AGENTS.md` 或 `CONVENTIONS.md`
- **GitHub Copilot**：读取仓库根指令
- **其他**：参考各工具的"项目级指令"机制

可选的 Claude Code hooks 占位见 [.claude/hooks/README.md](.claude/hooks/README.md)。

## CI 占位（验证层，非准入层）

- GitLab CI：[.gitlab-ci.yml](.gitlab-ci.yml)
- GitHub Actions：[.github/workflows/ci.yml](.github/workflows/ci.yml)

两个 CI 模板都使用 `<pm>` / `<runtime-image>` 占位符，请按项目实际包管理器和运行时替换。

**CI 是验证层，不是准入层**——CI 模板可在阶段 0 接入用于加固 verify 必跑纪律（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）。CI 跑出的结果可作为 verify 报告的事实证据；CI **不**替代 L3 Pre-Implementation Approval Gate（详见 [ADR-0005](docs/adr/0005-l3-approval-gate.md)，这是准入层）。

## 目录结构

```
.
├── AGENTS.md                       # 跨 AI 工具的统一入口
├── README.md                       # 本文件
├── CONTRIBUTING.md                 # 模板仓库维护说明
├── LICENSE                         # MIT
├── .gitignore
├── .claude/
│   ├── settings.json               # Claude Code 占位权限
│   └── hooks/README.md             # 占位 hooks 端口说明
├── docs/
│   ├── CONTEXT.md                  # 仓库术语表（新增）
│   ├── ai/                         # AI 治理与工作流
│   │   ├── context-index.md        # AI 会话入口导航
│   │   ├── governance-core.md      # 治理基线
│   │   ├── task-levels.md          # ★ 单点：L0-L3
│   │   ├── completion-criteria.md  # ★ 单点：完成定义
│   │   ├── verification-baseline.md# ★ 单点：验证基线
│   │   ├── branch-strategy.md      # ★ 单点：分支策略
│   │   ├── ai-role-boundaries.md   # ★ 单点：AI 边界
│   │   ├── doc-rewriting-rules.md  # ★ 单点：回写规则
│   │   ├── templates/
│   │   │   ├── task-packet.md
│   │   │   ├── feature-spec.md
│   │   │   ├── implementation-plan.md
│   │   │   ├── bugfix-brief.md
│   │   │   └── refactor-brief.md
│   │   ├── runbooks/
│   │   │   ├── l2-multi-session-runbook.md   # 通用 L2+ 4 session 纪律
│   │   │   ├── feature-delivery-runbook.md   # feature-specific
│   │   │   ├── bugfix-delivery-runbook.md    # bugfix-specific
│   │   │   ├── refactor-delivery-runbook.md  # refactor-specific
│   │   │   └── development-runbook.md
│   │   └── checklists/
│   │       └── review-checklist.md
│   ├── adr/                        # 长期决策
│   │   ├── 0001-task-level-governance.md  # 被 ADR-0004 修订 L2 段
│   │   ├── 0002-verify-hard-gate.md
│   │   ├── 0003-multi-session-l2.md
│   │   ├── 0004-l2-spec-and-plan.md
│   │   └── 0005-l3-approval-gate.md
│   ├── specs/                      # 单次任务设计（用户填充）
│   └── plans/                      # 实施计划（用户填充）
├── .gitlab-ci.yml                  # 占位 GitLab CI
└── .github/workflows/ci.yml        # 占位 GitHub Actions
```

## 维护与演进

本脚手架本身也是一个使用本治理的项目——修改它时：

- 触及长期边界、默认做法、跨工具兼容性时，按 [docs/ai/doc-rewriting-rules.md](docs/ai/doc-rewriting-rules.md) 回写文档
- 新增单点定义时，把已有的重复引用全部改链到新单点
- 修改前先看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

MIT。详见 [LICENSE](LICENSE)。
