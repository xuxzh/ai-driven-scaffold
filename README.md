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
# 仓库根 AGENTS.md 是脚手架本仓库专用，采用前先换成模板版
mv template/AGENTS.md AGENTS.md
```

### 方式 2：手动克隆并裁剪

```bash
git clone https://github.com/xuxzh/ai-driven-scaffold my-project
cd my-project
# 仓库根 AGENTS.md 是脚手架本仓库专用，采用前先换成模板版
mv template/AGENTS.md AGENTS.md
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
cp /tmp/ai-scaffold/template/AGENTS.md AGENTS.md

# 2. 如果项目还没有 docs/specs/ 和 docs/plans/，创建它们
mkdir -p docs/specs docs/plans
touch docs/specs/.gitkeep docs/plans/.gitkeep

# 3. 编辑 AGENTS.md 顶部的"用户项目元信息（Adoption Profile）"段落
#    把 5 个占位符（<pm> / <app-dir> / <entry-file> / <shared-dir> / <test-dir>）
#    替换为你的项目实际值

# 4. 清理临时克隆
rm -rf /tmp/ai-scaffold
```

> **注意**：`cp -r docs/ai docs/` 要求 `docs/` 目录已存在；如不存在，先 `mkdir -p docs/` 再复制。

### 接入后必做清理（三种方式通用）

`docs/specs/` 和 `docs/plans/` 在本脚手架自身演进时承载了脚手架的 spec/plan 历史（如 `adoption-self-check`、`scaffold-governance-tightening`）。这些是脚手架自身的演进记录，**不应**跟到你的目标项目。接入完成后：

```bash
# 保留 .gitkeep 作为空目录占位，删除其他所有历史文件
find docs/specs docs/plans -type f ! -name '.gitkeep' -delete
```

清理后两个目录应只剩 `.gitkeep`，等待你的目标项目首次 L2 任务生成 `docs/specs/<date>-<name>.md` 与 `docs/plans/<date>-<name>.md`。如果只想保留脚手架自身治理（不需要 docs/specs、docs/plans 这两个空目录），可以直接：

```bash
rm -rf docs/specs docs/plans
```

但**不推荐**——L2+ 任务需要它们承载 spec/plan 交付物，提前建好可避免后续流程卡壳。

## 接入后的 5 步

1. **补全 Adoption Profile**——编辑 `AGENTS.md` 顶部的"用户项目元信息（Adoption Profile）"，填入包管理器、命令、入口等
2. **必须定义 `verify` 命令**——在你项目的 manifest 中定义一个 `verify` 入口，串联 lint → typecheck → test → build；L1+ 任务完成前 AI 必跑（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）
3. **运行接入自检**——执行 `bash scripts/scaffold-doctor.sh`（等价于 `--adopted`），并按 [adoption-checklist.md](docs/ai/checklists/adoption-checklist.md) 处理 `FAIL` / `WARN`；doctor 只检查脚手架接入状态，不替代项目 `verify`
4. **跑一次 L0 任务试水**——用本文档试一次小改动，跑一次最小验证
5. **跑一次 L2 任务验证流程**——按 [l2-multi-session-runbook.md](docs/ai/runbooks/l2-multi-session-runbook.md) + [feature-delivery-runbook.md](docs/ai/runbooks/feature-delivery-runbook.md) 跑通一次新功能（3 session 串行：规划 → 实施 → 评审；spec + plan 物理分离，验证证据统一落点到两份文件）

> **已取代**：本节原表述为"4 session 串行：设计 → 计划 → 实施 → 评审"——该 4 Session 措辞将 L2 与 L3 合并为同一模型，与 [ADR-0003](docs/adr/0003-multi-session-l2.md) 2026-08-01 修订（**L2 = 三 Session；L3 = 四 Session**）不相容。现行 L2 流程以本节首段为准。

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
  - [ADR-0003 L2 三 Session / L3 四 Session](docs/adr/0003-multi-session-l2.md)
  - [ADR-0004 L2 spec + plan](docs/adr/0004-l2-spec-and-plan.md)
  - [ADR-0005 L3 审批门禁](docs/adr/0005-l3-approval-gate.md)

## 模板与清单

- 任务包（L1）：[docs/ai/templates/task-packet.md](docs/ai/templates/task-packet.md)
- 功能设计（L2 spec）：[docs/ai/templates/feature-spec.md](docs/ai/templates/feature-spec.md)
- 实施计划（L2 plan）：[docs/ai/templates/implementation-plan.md](docs/ai/templates/implementation-plan.md)
- 缺陷修复：[docs/ai/templates/bugfix-brief.md](docs/ai/templates/bugfix-brief.md)
- 重构：[docs/ai/templates/refactor-brief.md](docs/ai/templates/refactor-brief.md)
- 接入自检清单：[docs/ai/checklists/adoption-checklist.md](docs/ai/checklists/adoption-checklist.md)
- 评审清单：[docs/ai/checklists/review-checklist.md](docs/ai/checklists/review-checklist.md)
- ADR 模板：[docs/adr/adr-template.md](docs/adr/adr-template.md)

## 跨 AI 工具兼容

本脚手架的核心约束通过 `AGENTS.md` 入口表达，被以下 AI 工具自动识别：

- **Claude Code**：直接读取 `AGENTS.md`
- **Cursor**：读取 `AGENTS.md` 或 `.cursorrules`
- **Aider**：读取 `AGENTS.md` 或 `CONVENTIONS.md`
- **GitHub Copilot**：读取仓库根指令
- **其他**：参考各工具的"项目级指令"机制

> 仓库根 `AGENTS.md` 是**本仓库专用**入口（已按脚手架自身事实填好 Adoption Profile）；采用本脚手架的项目的模板在 [`template/AGENTS.md`](template/AGENTS.md)，三种接入方式都会先把它替换到根。

本脚手架不提供任何 AI 工具专属配置。L3 审批、verify 必跑和多 session 串行等约束都通过 `AGENTS.md`、`docs/ai/` 与 `docs/adr/` 表达；具体工具的 hook、rule 或插件只能作为项目自行添加的可选加固层。

## CI（验证层，非准入层）

- GitLab CI：[.gitlab-ci.yml](.gitlab-ci.yml)
- GitHub Actions：[.github/workflows/ci.yml](.github/workflows/ci.yml)

CI 跑 5 个 job：`lint-shell` / `lint-python` / `check-links` / `check-governance` / `check-doctor`。零第三方依赖，Python 3 标准库 + POSIX bash 即可执行。

**CI 是验证层，不是准入层**——CI 跑通只证明脚手架自身检查器与脚本在干净环境下能跑通，**不**等价于 L3 Pre-Implementation Approval Gate（详见 [ADR-0005](docs/adr/0005-l3-approval-gate.md)，那是准入层）。CI 结果可作为 L1+ 任务 verify 报告的事实证据（详见 [ADR-0002](docs/adr/0002-verify-hard-gate.md)）。

### 维护者跑哪些本地命令等价于 CI 行为

维护本脚手架仓库的开发者，本地跑通下面这一组命令即等价于 CI 5 个 job 全部通过：

```bash
# lint-shell —— bash 语法校验（不执行）
bash -n scripts/scaffold-doctor.sh
bash -n scripts/worktree-add.sh
bash -n scripts/hooks/rewrite-worktree-add.sh

# lint-python —— Python 检查器与单测
python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v

# check-links —— Markdown 相对链接检查（template 模式）
python3 scripts/check-markdown-links.py --root . --template

# check-governance —— 治理规则一致性（GOV001-GOV004）
python3 scripts/check-governance-consistency.py --root . --template

# check-doctor —— 聚合自检 + 集成测试
bash scripts/scaffold-doctor.sh --template
bash scripts/tests/scaffold-doctor-test.sh
bash scripts/tests/worktree-add-test.sh
```

`--template` 模式适用于**本脚手架仓库自身**（仓库根 `AGENTS.md` 的 Adoption Profile 已按本仓库事实填好）。接入本脚手架的**目标项目**跑默认模式即可（`bash scripts/scaffold-doctor.sh`，等价于 `--adopted`，会额外检查 4 档验证入口是否映射到 manifest）。两种模式的差异见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 doctor 顶部的 `--adopted|--template` 说明。

## 目录结构

```
.
├── AGENTS.md                       # 本仓库专用入口（采用者模板在 template/AGENTS.md）
├── README.md                       # 本文件
├── CONTRIBUTING.md                 # 模板仓库维护说明
├── LICENSE                         # MIT
├── .gitignore
├── scripts/
│   └── scaffold-doctor.sh          # 只读接入自检脚本
├── template/
│   └── AGENTS.md                   # 采用本脚手架的项目复制源（含 5 个 <...> 占位符）
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
│   │   │   ├── l2-multi-session-runbook.md   # 通用 L2 三 Session 纪律（规划/实施/评审）；L3 在此基础上叠加设计+计划双 Session（共四 Session）与实施前明确批准
│   │   │   ├── feature-delivery-runbook.md   # feature-specific
│   │   │   ├── bugfix-delivery-runbook.md    # bugfix-specific
│   │   │   ├── refactor-delivery-runbook.md  # refactor-specific
│   │   │   └── development-runbook.md
│   │   └── checklists/
│   │       ├── adoption-checklist.md
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
- 维护模板仓库时使用 `bash scripts/scaffold-doctor.sh --template`；接入目标项目时使用默认 `bash scripts/scaffold-doctor.sh`
- 修改前先看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

MIT。详见 [LICENSE](LICENSE)。
