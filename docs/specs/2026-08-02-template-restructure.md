# 把所有下发物物理收拢到 `template/` 下

> L2 设计 spec。L2 任务必须先按本 spec 产出 `docs/specs/<date>-<name>.md`,用户确认后再按 [implementation-plan.md](../../ai/templates/implementation-plan.md) 模板产出 `docs/plans/<date>-<name>.md`;spec 与 plan 是两份独立文件(详见 [ADR-0003](../../adr/0003-multi-session-l2.md) 与 [ADR-0004](../../adr/0004-l2-spec-and-plan.md))。
>
> **本 spec 不写执行切片**——任务切片、步骤、命令、文件清单、回滚路径属于 plan,不在本文件范围(详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md) 的"spec 与 plan 最小接口"段)。

## 元信息

- 主题：restructure, template, scaffold, governance, paths
- 状态：draft
- 关联 ADR：(无直接引用;沿用 ADR-0002 / 0003 / 0004 既有硬门禁)

## 背景

本仓库作为"语言无关的 AI 驱动开发治理脚手架",自身同时承担两个身份:

1. **脚手架自身**——`AGENTS.md` 入口已填本仓库的 Adoption Profile,`docs/specs/` `docs/plans/` 承载本仓库的 L2 演进历史,`README.md` `CONTRIBUTING.md` `LICENSE` `.gitignore` 是仓库维护者用的。
2. **下发物**——`template/AGENTS.md` 等采用者会复制的文件;采用者拿走后,通过 `cp -r` 等命令把它们安置到目标项目。

当前问题:除 `AGENTS.md` 之外,**所有下发物都散落在根目录**:

| 下发物 | 当前路径 | 是否已显式归入 `template/` |
|---|---|---|
| `AGENTS.md` | `template/AGENTS.md` | ✅ |
| `docs/ai/**` | `docs/ai/**` | ❌ |
| `docs/adr/**` | `docs/adr/**` | ❌ |
| `docs/CONTEXT.md` | `docs/CONTEXT.md` | ❌ |
| `scripts/**` | `scripts/**` | ❌ |
| `.gitlab-ci.yml` | `.gitlab-ci.yml` | ❌ |
| `.github/workflows/ci.yml` | `.github/workflows/ci.yml` | ❌ |
| `CLAUDE.md` | `CLAUDE.md` | ❌ |

只有 `AGENTS.md` 因为有 5 个 Adoption Profile 占位符被独立成"模板版",其余下发物靠 README "方式 3" 的 `cp -r` 命令逐项复制——边界是**文本约定**,目录上看不出来。

为什么现在启动:本仓库在 GOV 收敛(见 [docs/plans/2026-08-01-ai-governance-rule-convergence.md](../../plans/2026-08-01-ai-governance-rule-convergence.md))之后,治理文档数量趋于稳定,适合做"目录与语义同步"的结构整理;后续任何新增的下发物(单点定义、runbook、检查器)都能直接落在 `template/` 下,避免再出现"该进 template 还是留在根"的两难。

## 目标

把所有"采用者会拿到"的文件物理收拢到 `template/` 目录下,让"脚手架自身"和"采用者会拿到"在目录结构上**一眼可分**;同时保证下游采用流程、doctor 校验、CI 占位等行为不变。

## 行为

迁移后的目录结构:

```text
<repo-root>/
├── AGENTS.md                          # 脚手架自身(已填 Adoption Profile)
├── README.md                          # 脚手架自身(对外介绍)
├── CONTRIBUTING.md                    # 脚手架自身(维护者用)
├── LICENSE                            # 脚手架自身
├── .gitignore                         # 脚手架自身
├── docs/
│   ├── specs/                         # 脚手架自身 L2 历史
│   └── plans/                         # 脚手架自身 L2 历史
└── template/                          # 下发物
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── docs/
    │   ├── ai/
    │   ├── adr/
    │   └── CONTEXT.md
    ├── scripts/
    └── .github/workflows/ci.yml
    └── .gitlab-ci.yml
```

行为变化清单:

- **采用流程(方式 1/2)**:`cp -rT template .` 一次性拿到所有下发物,旧 README 里的 6 条独立 `cp` 命令消失。
- **采用流程(方式 3)**:6 条 `cp` 命令路径前缀从 `docs/` 改成 `template/docs/`,新增 4 条新文件复制。
- **脚手架自身 L1+ 验证**:`scripts/...` 路径全部改成 `template/scripts/...`。
- **doctor**:`--template` 模式检查 `template/` 下文件存在性;`--adopted` 模式检查根下文件存在性(沿用现状,无新增模式)。
- **CI 文件**:`template/.github/workflows/ci.yml` 和 `template/.gitlab-ci.yml` 内容**保持**对 `scripts/...` 的引用——这些文件是给采用者用的,采用者复制后 CI 在根、scripts 也在根,相对路径正确;脚手架自身的"本地等价 CI 命令"通过 `template/scripts/...` 路径走,写在 README/CONTRIBUTING 的维护者段落。
- **`docs/CONTEXT.md`**:之前未在采用步骤中显式列出,迁移后从 `template/docs/CONTEXT.md` 复制,采用者无感但补齐了漏掉的术语表下发。

## 非目标

- **不动治理语义**——任务分级、验证基线、提交规范、ADR 内容、Isolation Profile、Strict Isolation 选项全部不变。
- **不改任何"已下发内容"的文字**——`docs/ai/`、`docs/adr/`、`docs/CONTEXT.md` 内部文字、链接结构保持不变,只做物理平移(其内部相对引用平移后仍然正确,无需修改)。
- **不引入新特性**——不写 `--adopt` 模式、不加新的 doctor 检查器、不加 bootstrap 脚本、不改 `worktree-add.sh` 的 prefix 强制规则。
- **不解决 `branch-strategy.md` 与 `worktree-add.sh` 的 prefix 分隔符分歧**(slash vs hyphen,见 [scripts/worktree-add.sh](../../worktree-add.sh) 顶部注释)。本次迁移按 `worktree-add.sh` 实际接受的 `refactor/template-restructure` 走。
- **不处理既有项目里 `.github/` 已有 workflows 的自动合并**——README 提示用户手动 `diff` 处理。
- **不重写 `docs/specs/` `docs/plans/` 的内容**——只更新其中的相对路径引用。
- **不动 `.gitignore`**——保留在根,后续由 doctor 在 `adopted` 模式下检查/生成(不在本次范围)。

## 验收(外部可判据)

每条都以"满足 X 即验收"形式给出,可被独立判断。

### 结构层

- 在 `template/` 下能找到 8 项:`AGENTS.md`、`CLAUDE.md`、`docs/ai/`、`docs/adr/`、`docs/CONTEXT.md`、`scripts/`、`.github/workflows/ci.yml`、`.gitlab-ci.yml`。
- 根目录下不再有 `docs/ai/`、`docs/adr/`、`docs/CONTEXT.md`、`scripts/`(以 `git ls-tree HEAD --name-only` 视角)。
- 根 `docs/` 下只剩 `specs/` `plans/`。
- 根 `AGENTS.md`、`README.md`、`CONTRIBUTING.md`、`LICENSE`、`.gitignore` 保留。

### 引用层

- 根 `AGENTS.md`、`README.md`、`CONTRIBUTING.md`、`docs/specs/**`、`docs/plans/**` 里所有 `docs/ai/`、`docs/adr/`、`docs/CONTEXT.md`、`scripts/`、`.gitlab-ci.yml`、`.github/workflows/` 引用应指向 `template/...`。
- 根 `.md` 中不应有 `../docs/` 形式的链接残留(可在 grep 中验证)。
- `template/AGENTS.md`、`template/CLAUDE.md` 内的相对引用应去掉 `../` 前缀(改用 `docs/ai/...` 等)。

### 工具层(以下命令在 repo 根执行,退出码 0)

- `bash template/scripts/scaffold-doctor.sh --template`
- `python3 template/scripts/check-markdown-links.py --root . --template`
- `python3 template/scripts/check-governance-consistency.py --root . --template`
- `python3 template/scripts/check-spec-and-plan-naming.py`
- `bash template/scripts/tests/scaffold-doctor-test.sh`
- `bash template/scripts/tests/worktree-add-test.sh`
- `python3 -m unittest discover -s template/scripts/tests -p 'test_*.py' -v`

### 端到端层

- 在 `/tmp` 跑方式 1 全流程(用 `cp -rT` 替代 `gh repo create`),新仓库根 `bash scripts/scaffold-doctor.sh` 应输出采用者自检结果(doctor 自身视角正确切换)。
- 新建仓库根不应包含 `template/`、`docs/specs/` `docs/plans/` 脚手架自身历史文件。

## 范围级别

- **建议任务级别**：`L2`
- **为什么适用这个级别**:
  - 跨多个目录结构的物理重排,涉及 8 项文件/目录搬迁、30+ 路径引用改写、doctor 内部硬编码路径常量更新、README 三种接入方式改写。
  - 影响"数据流"(链接解析)与"入口"(README、doctor、CI),符合 L2 在 [task-levels.md](../../ai/task-levels.md) 中的定义。
  - 不触及鉴权、依赖、CI 策略本身,不需要 L3 批准门禁。

## 受影响边界

- **物理布局**:根 `docs/` 下只剩 `specs/` `plans/`,其它治理文档移入 `template/docs/`;根 `scripts/` 消失,移入 `template/scripts/`;根 CI 文件移入 `template/.github/` 和 `template/.gitlab-ci.yml`;根 `CLAUDE.md` 移入 `template/`。
- **路径引用**:全仓 markdown 相对链接;CI 脚本对 `scripts/` 的引用;README "方式 1/2/3" 的 `cp` 命令;脚手架自身 L1+ 验证命令。
- **工具链**:`scripts/scaffold-doctor.sh` 内部对 `docs/ai/`、`scripts/` 的硬编码路径常量;`scripts/check-*.py` 对 `docs/` 的引用;`scripts/tests/*.sh` 对脚本路径的引用。
- **边界语义**:脚手架自身 vs 下发物的边界从"README 文字约定"升级为"目录物理分隔"。
- **采用流程**:README 三种接入方式全部改写;`docs/CONTEXT.md` 等原本未在采用步骤中列出的项目现在也包含进来。
- **CI 占位**:`template/.github/workflows/ci.yml` 和 `template/.gitlab-ci.yml` 内容**不变**(它们对 `scripts/` 的引用在采用者视角下正确),脚手架自身不跑这两份 CI(走本地等价命令)。

## 建议方案

详细设计已在与用户的三轮 brainstorming 中逐节确认;本段是浓缩索引,具体实施切片属于 plan。

### 文件清单 8 项(7 搬迁 + 1 不动,来自 Section 1)

| 路径 | 目标路径 | 类别 |
|---|---|---|
| `docs/ai/**` | `template/docs/ai/**` | 下发 |
| `docs/adr/**` | `template/docs/adr/**` | 下发 |
| `docs/CONTEXT.md` | `template/docs/CONTEXT.md` | 下发 |
| `scripts/**` | `template/scripts/**` | 下发 |
| `.gitlab-ci.yml` | `template/.gitlab-ci.yml` | 下发 |
| `.github/workflows/ci.yml` | `template/.github/workflows/ci.yml` | 下发 |
| `CLAUDE.md`(根) | `template/CLAUDE.md` | 下发 |
| `.gitignore`(根) | (不动) | 脚手架自身,后续由 doctor 处理 |

### 路径/链接修复 3 条 sed 规则(来自 Section 2)

- **规则 1**:`template/AGENTS.md`、`template/CLAUDE.md` 里 `../docs/` → `docs/`(去掉 `../`,改成同级引用)。
- **规则 2**:根所有 `.md`(`AGENTS.md`、`README.md`、`CONTRIBUTING.md`、`docs/specs/**`、`docs/plans/**`)里 `docs/ai/` `docs/adr/` `docs/CONTEXT.md` `scripts/` `.gitlab-ci.yml` `.github/workflows/` 前缀加 `template/`。
- **规则 3**:`template/docs/**` 内部互引保持不变(平移后相对路径仍然正确)。

**为什么这套方案符合当前仓库的既有模式**:

- 用 `git mv` 平移,保留 git rename detection(避免 PR diff 退化为"删除 + 新增")。
- sed 一次性扫,加一遍人工审计 + `check-markdown-links.py` 自动验证,组合已成仓库 `docs-` 任务的标准收尾方式。
- 不引入新检查器:既有的 `check-markdown-links.py` + `check-governance-consistency.py` 已能 fail 任何相对链接解析不到的目标,新 invariant 冗余。

### 流程与工具更新(来自 Section 3)

- README "5 分钟上手" 三方式按新路径改写(详见"采用流程"段,具体 cp 命令属于 plan)。
- 删除 README "接入后必做清理" 段——脚手架自身 spec/plan 历史留在根 `docs/specs/` `docs/plans/`,采用者拿不到那段历史,清理说明整段作废。
- doctor 脚本 `--template` / `--adopted` 模式检查路径表按新结构更新(详见 plan 的执行切片)。
- 根 `AGENTS.md` 顶部保留本仓库的 Adoption Profile(已填),只需改内部链接。
- `template/AGENTS.md` 的 5 个 `<...>` 占位符保持原状(仍是采用者填空的入口)。

## 备选方案

- **方案 A:保持现状 + 下发清单**
  - 不搬任何文件,只在 `template/` 下加 `MANIFEST.md` 显式说明"以下文件会被采用者复制"。
  - **未采用原因**:目录上仍是"混居",边界靠文本约定——只是把"散落在根目录"换成了"散落在根 + 一份 manifest 提示",没有解决用户的核心痛点("一眼分不清")。
- **方案 C:折中:根 `docs/ai` 保留,`template/` 加 symlink farm**
  - `template/docs/ai` → `docs/ai`、`template/docs/adr` → `docs/adr` 等等。
  - **未采用原因**:Windows 兼容性差;引入"软链抽象层"与脚手架"零配置、零依赖"的原则相悖;L1+ 工作区在 Windows + WSL 混用时易踩坑。

## 验证计划(策略层)

> 本段写"什么算合格",具体命令属于 plan 的 `## 验证证据` 段。

- **结构层验证**:`git ls-tree HEAD --name-only` 应能枚举出验收段"结构层"列出的所有路径。
- **引用层验证**:`rg "../docs/"` 在根 `.md` 中应无输出(根 `.md` 不应有 `../docs/` 形式链接);`rg "docs/ai" AGENTS.md README.md CONTRIBUTING.md` 应输出形如 `template/docs/ai/...` 的链接。
- **工具层验证**:跑 `## 验收 / 工具层` 列出的 7 条命令,全部退出码 0。
- **端到端验证**:在 `/tmp/adopt-smoke` 跑方式 1 全流程(用 `cp -rT template .` 替代 `gh repo create`),再跑 `bash scripts/scaffold-doctor.sh`,确认 doctor 走 `--adopted` 模式且输出采用者自检结果;并确认 `/tmp/adopt-smoke` 下不再包含 `template/` 目录本身。
- **e2e 覆盖**:不需要 e2e(无运行时),只需要上面 4 层。

## 风险

- **路径遗漏**:手改路径常量遗漏会导致 doctor 误报或 markdown 链接破。**mitigation**:7 条验证命令全跑 + `check-markdown-links.py` 零破链是硬门禁;在 plan 阶段把 doctor 内部路径常量单列一张"路径迁移映射表",逐条 review。
- **`shopt -s dotglob` 跨 shell 行为差异**:macOS 默认 zsh 支持,但 fish / 其他 shell 不支持。**mitigation**:README 在 `cp -rT` 命令前加一句"用 bash 跑这串",不写死 `shopt`。
- **方式 3 的 `.github/` 合并覆盖既有 workflows**:`cp -r` 会覆盖。**mitigation**:用 `cp -rn` no-clobber;README 显式写"先 `diff` 再决定合并";不在本次范围提供自动合并工具。
- **CI 路径双视角**:`template/.github/workflows/ci.yml` 写 `scripts/...` 是为采用者服务(采用后都在根),脚手架自身本地等价命令需走 `template/scripts/...`。**mitigation**:README 维护者段落分两块写"采用者视角 vs 维护者视角"命令,各跑各的路径。
- **git 历史可读性**:大量 `git mv` 重命名,git 默认能识别重命名,但 PR diff 在 `git log -p` 视角下可能呈现"删除 + 新增"而非重命名。**mitigation**:全部用 `git mv` 不用 `rm + add`,保留 rename detection;在 PR 描述里写明"本 PR 主要为文件重命名,行为不变"。
- **spec/plan 历史里残留旧路径**:`docs/specs/2026-08-01-*.md` 等脚手架自身的 L2 历史里若引用了 `docs/ai/...`,sed 规则 2 会扫到并加 `template/` 前缀——这是预期行为,但会让这些历史 spec/plan 看起来"超前"(引用了未来的路径)。**mitigation**:在 plan 阶段单独说明"这是迁移后的统一新路径引用,不是回写 spec 内容";不动 spec 文本,只改链接。
- **prefix 分隔符分歧**(见"非目标"):本任务按 `worktree-add.sh` 实际接受的 `refactor/template-restructure` 走,临时不与 `branch-strategy.md` 同步;后续如需统一,需另起 L2 任务修文档+脚本。

## 需要更新的文档

- **`AGENTS.md`(根)**:内部链接加 `template/` 前缀;Adoption Profile 表本身不变(仍是本仓库自用版的填法)。
- **`README.md`(根)**:三方式改写 + 删"接入后必做清理"段 + 维护者段落写两块命令(采用者 vs 维护者)。
- **`CONTRIBUTING.md`(根)**:维护者命令路径改 `template/scripts/...`;CI 等价命令段同步更新。
- **`docs/specs/**`、`docs/plans/**`**:脚手架自身 L2 历史里的所有 `docs/...` `scripts/` 引用加 `template/` 前缀;spec/plan 文本内容不动。
- **`template/AGENTS.md`、`template/CLAUDE.md`**:链接去掉 `../` 前缀(规则 1)。
- **不更新**:
  - `docs/ai/**` 内部互引(平移不变,规则 3)
  - `docs/adr/*`(ADR 描述的是治理规则,跟文件位置无关)
  - `docs/CONTEXT.md`(平移不变)
  - `template/docs/CONTEXT.md`(同 `docs/CONTEXT.md`)
  - `scripts/` 内脚本(sed 改不到的手改项在 plan 里单列,不在本 spec 范围)
  - `docs/ai/branch-strategy.md` 的 prefix 列表(本次不修 prefix 分歧)
  - `docs/adr/0005-l3-approval-gate.md` 等 ADR 内容(本次不动治理语义)

## Session Handoff

按 [`session-handoff-protocol.md`](../../ai/runbooks/session-handoff-protocol.md) 11 字段填。

- **Task Level**: L2
- **Current Phase**: spec 撰写完成,等待用户 review
- **Status**: active
- **Completed**:
  - Section 1 拍板:8 项文件搬迁 + `.gitignore` 留在根
  - Section 2 拍板:3 条 sed 规则 + 现有 checker 验证 + 不加新 invariant + CI 路径双视角
  - Section 3 拍板:README 三方式改写、doctor 两种模式路径表、7 条验证命令、3 个风险点
  - 创建 worktree `refactor/template-restructure` 在 `.worktrees/refactor-template-restructure/`
  - 写本 spec 到 `docs/specs/2026-08-02-template-restructure.md`
- **Artifacts**:
  - `docs/specs/2026-08-02-template-restructure.md`(本文件,commit 后待 review)
  - worktree: `.worktrees/refactor-template-restructure/`,branch: `refactor/template-restructure`
- **Decisions**:
  - 走方案 B(把所有下发物物理收拢到 `template/`),不方案 A/C
  - `docs/CONTEXT.md` 算下发物(Q1–Q4 未单独讨论,根据 README 目录结构段 + 术语表性质推断)
  - `.gitignore` 留在根,后续由 doctor 在 `adopted` 模式处理(Q2 b)
  - `scripts/` 全部进 `template/scripts/`,不拆(Q3 a)
  - 所有相对路径引用都改写,不留旧路径(Q4)
  - sed 3 条规则 + 现有 checker 验证,不加新 invariant
  - CI 文件保持 `scripts/...` 引用,README 维护者段落写双视角
  - 本任务不解决 `branch-strategy.md` 与 `worktree-add.sh` 的 prefix 分隔符分歧
  - 本任务不引入 `--adopt` 模式 / bootstrap 脚本
- **Assumptions**:
  - `template/.github/workflows/ci.yml` 写 `scripts/...` 在采用者视角下解析正确(采用后 CI 在根、scripts 也在根)
  - `cp -rT template .` 在 macOS 默认 zsh / bash 下行为一致(行为已确认)
  - `worktree-add.sh` 的 prefix slash 格式(`refactor/template-restructure`)长期有效,不会在实施 session 前被改回 hyphen
  - 当前 `template/AGENTS.md` 5 个 `<...>` 占位符保留原状(仍是采用者填空的入口)
  - `docs/specs/**` `docs/plans/**` 里的旧路径引用被 sed 规则 2 改写是预期行为(不会破坏 spec/plan 语义,只改链接)
- **Open Questions**:
  - 无阻塞问题;如用户在 review 中提出新需求,会进入"Open Questions"或"Assumptions 更新"
- **Verification**:(实施 session 跑完后填,规划 session 不允许填——本字段留空指针)
- **Next Allowed Actions**:
  - 用户 review 本 spec,确认或提出修改
  - 用户确认后,本 session 调 writing-plans skill 写 `docs/plans/2026-08-02-template-restructure.md`
  - 计划 session 跑完后,等用户明确开始实施信号
- **Prohibited Scope**:
  - 不得修改 `docs/adr/*` 的内容(只搬不改)
  - 不得修改 `docs/ai/**` 内部链接(平移不变)
  - 不得修改 `template/AGENTS.md` 的 5 个 `<...>` 占位符
  - 不得引入 `--adopt` 模式 / bootstrap 脚本
  - 不得修 `branch-strategy.md` 与 `worktree-add.sh` 的 prefix 分歧
  - 不得在 `main` 上提交;只允许在 `refactor/template-restructure` 分支上提交

## 批准(L3 任务必填)

- 不适用——本任务为 L2,不需要 Pre-Implementation Approval Gate(详见 [ADR-0005](../../adr/0005-l3-approval-gate.md))。

## 验证证据(实施 session 末尾必填)

- 不适用——本 spec 由规划 session 产出,实施 session 跑完 `verify` 入口后填写。
