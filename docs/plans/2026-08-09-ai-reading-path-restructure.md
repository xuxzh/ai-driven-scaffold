# AI 阅读路径重构实施计划

> 基于 spec：[docs/specs/2026-08-09-ai-reading-path-restructure.md](../specs/2026-08-09-ai-reading-path-restructure.md)
> （此行**必填**，否则视为与 spec 失联，详见 [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md)）

## 元信息

- 主题：reading-path, layering, navigation, governance, dedup
- 状态：`draft`
- 关联 ADR：沿用 [ADR-0002](../../template/docs/adr/0002-verify-hard-gate.md) / [ADR-0003](../../template/docs/adr/0003-multi-session-l2.md) / [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md)；Task 7 新增 ADR-0006

> 命名规范见 [spec-and-plan-naming.md](../../template/docs/ai/spec-and-plan-naming.md)；文件名前缀为 `<date>-<name>.md`。

> **面向 Agent 执行者**：步骤使用复选框 `- [ ]` 跟踪；本 plan 在 worktree `refactor-ai-reading-path` 上执行，由实施 session 按 Task 0 → 7 顺序推进，每 Task 末尾一个独立 commit，每 Task 末尾验证必须全绿才进下一 Task。

**任务概述（限 2-3 句）**：把 AI 阅读路径从"线性通读 11 链"重构为"四层分离 + 分流入口"。先重构 `AGENTS.md`（根 + template 两份）移除对 summary 的全部引用，再补 TL;DR 并删 4 个 summary 文件，随后去规则化 context-index、降级 ADR、去重外围 runbook、修断链、新增 ADR-0006。分 8 个 Task 推进，每 Task 一个独立可验证交付物。

## 文件清单

**新建**：

- `template/docs/adr/0006-reading-path-layering.md`（Task 7）

**修改**：

- `AGENTS.md`（根；Task 1 删治理入口段 + 任务速查表 + 文档分层速记，加分流表）
- `template/AGENTS.md`（模板版；Task 1 同步改动，路径用 `docs/ai/...` 相对前缀）
- `template/docs/ai/context-index.md`（Task 3 去规则化 + 吸收路径唯一权威）
- `template/docs/ai/task-levels.md`（Task 2 补 TL;DR；Task 3 收口准入门禁）
- `template/docs/ai/branch-strategy.md`（Task 2 补 TL;DR）
- `template/docs/ai/verification-baseline.md`（Task 2 补 TL;DR）
- `template/docs/ai/completion-criteria.md`（Task 2 补 TL;DR）
- `template/docs/ai/commit-convention.md`（Task 2 补 TL;DR + 删反向指向 summary 的链接）
- `template/docs/ai/governance-core.md`（Task 4 ADR 降级 + 删单点索引里的 summary 链接）
- `template/docs/ai/ai-role-boundaries.md`（Task 4 ADR 引用改按需）
- `template/docs/ai/doc-rewriting-rules.md`（Task 5 补"TL;DR 同源同步"提示）
- `template/docs/ai/l2-multi-session-runbook.md`（Task 5 去重段改"复制→引用+增量"）
- `template/docs/CONTEXT.md`（Task 6 消除 AGENTS.md 双链接歧义）
- `template/docs/ai/dogfood/2026-08-ai-governance-v2-report.md`（Task 6 加快照水印）
- `template/docs/ai/dogfood/2026-08-batch-drill.md`（Task 6 加快照水印）
- `template/docs/ai/dogfood/2026-08-l2-handoff-drill.md`（Task 6 加快照水印）
- `template/docs/adr/README.md`（Task 7 索引补 ADR-0006）
- `docs/plans/2026-08-01-ai-session-batch-and-dogfood.md`（Task 2 把对 summary 的引用改指向 full）

**删除**：

- `template/docs/ai/context-index-summary.md`
- `template/docs/ai/task-levels-summary.md`
- `template/docs/ai/branch-strategy-summary.md`
- `template/docs/ai/commit-convention-summary.md`

**测试**（都已存在，本 plan 不新增）：

- `bash template/scripts/scaffold-doctor.sh --template`
- `python3 template/scripts/check-markdown-links.py --root . --template`
- `python3 template/scripts/check-governance-consistency.py --root . --template`

## 全局约束

（本段从 spec 摘录，所有 Task 隐含适用。）

- **任务等级**：L2，spec 已由用户确认（会话消息"确认 spec，继续 plan"），plan 产出后进入实施 session。
- **工作区**：独立 worktree `.worktrees/refactor-ai-reading-path/`，分支 `refactor-ai-reading-path`；**严禁**在 `main` 提交。
- **commit 规范**：Conventional Commits；type 主要用 `refactor`（路径重构不改治理语义）与 `docs`（补 TL;DR / 水印）；scope 落在路径主段（`agents` / `context-index` / `governance` / `runbooks` / `adr`）。
- **不修改**：任何治理文件的"规则语义"——任务分级条件、验证档位语义、提交规范实质规则、ADR 决策结论、Adoption Profile 10 字段、模板骨架字段。本 plan 只动"规则如何被找到与读取"。
- **不引入新机制**：不新增 CI 门禁、doctor 检查器、bootstrap 脚本。
- **验证入口**：3 条命令（doctor / link / governance），每 Task 末尾跑，全退出码 0 才进下一 Task。
- **两处 spec Open Question 的默认决策**（用户未单独回复，本 plan 采用如下默认，评审 session 可调整）：
  - TL;DR 段统一用 `## TL;DR` 二级标题（理由：进目录树、可被 `rg '^## TL;DR'` 检索、与单点文件现有 `## 目的` / `## 关联` 标题风格一致）。
  - 分流表只按 L 级别分流（L0/L1/L2/L3）；session 角色分流交给 `context-index.md` 深路径段承载（理由：AGENTS.md 入口保持轻量，二维表会让入口过重）。
- **spec 遗漏的额外引用点**（plan 摸清）：`docs/plans/2026-08-01-ai-session-batch-and-dogfood.md` 引用了全部 4 个 summary，删 summary 后会断链——Task 2 把这些引用改指向 full（属 spec"受影响边界·路径引用"的落实，不偏离 spec）。

---

### Task 0（基线）：记录迁移前对照点

> worktree 已建立且 baseline 已跑通（spec 阶段 0 fail / 0 warning）。本 Task 仅把基线记入 `## 验证证据` 表，作为"重构前对照点"。

- [ ] **步骤 1：跑 3 条验证命令，记退出码与关键输出**

从 worktree 根 `.worktrees/refactor-ai-reading-path` 执行：

```bash
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0；doctor 输出 `Summary: 0 fail(s), 0 warning(s)`。

- [ ] **步骤 2：把 3 条命令的退出码与关键输出记入本 plan 末尾 `## 验证证据` 表的"基线"行**

- [ ] **步骤 3：无 commit**

本 Task 不产生 commit，只作为对照点。

---

### Task 1（P0）：AGENTS.md 入口重构（根 + template 两份）

**目标**：移除 `AGENTS.md`（根）与 `template/AGENTS.md`（模板版）对 4 个 summary 的全部引用，并重建入口为"硬边界 + 分流表"。

**文件：**

- 修改：`AGENTS.md`（根）、`template/AGENTS.md`（模板版）

- [ ] **步骤 1：改动前状态断言**

```bash
# 根 AGENTS.md 治理入口段应命中"按以下顺序阅读" + 4 个 summary 链接
rg -c "按以下顺序阅读" AGENTS.md            # 预期 ≥1
rg -c "summary\.md" AGENTS.md               # 预期 ≥4（4 个 summary）
rg -c "summary\.md" template/AGENTS.md      # 预期 ≥4
rg -c "任务入口速查|文档分层速记" AGENTS.md  # 预期 ≥1
```

- [ ] **步骤 2：实现改动**

对 `AGENTS.md`（根）与 `template/AGENTS.md`（模板版）执行：

1. 删除"治理入口"段（含"按以下顺序阅读"的 11 链通读清单，含对 4 个 summary 的链接）。
2. 删除"任务入口速查"短摘要表与"文档分层速记"表（这两项职责归导航层 context-index）。
3. 保留：顶部"本文件是仓库级统一入口"说明、"AI 工作规则（执行前必读）"10 条硬边界、"用户项目元信息"段（根版已填、template 版保留占位符）、"重要边界（不要破坏）"段。
4. 在"AI 工作规则"段之后、"用户项目元信息"段之前，新增"## 分流入口"段，写入 spec 的分流决策表（L0/L1/L2/L3 × 本次必读集 × 触发型），作为入口唯一权威。表述注明"先回答改动级别（见 task-levels 判定三问），按下表取本次必读集；触发型文件发生对应行为时再读"。
5. 路径差异：根版用 `template/docs/ai/...` 前缀；template 版用 `docs/ai/...` 相对前缀。

- [ ] **步骤 3：改动后验证**

```bash
# 治理入口通读清单与 summary 引用应已消失
rg -c "按以下顺序阅读" AGENTS.md            # 预期 0（无命中）
rg -c "summary\.md" AGENTS.md               # 预期 0
rg -c "summary\.md" template/AGENTS.md      # 预期 0
rg -c "任务入口速查|文档分层速记" AGENTS.md  # 预期 0
# 分流入口表应已就位
rg -c "## 分流入口" AGENTS.md               # 预期 1
rg -c "## 分流入口" template/AGENTS.md      # 预期 1
# 3 条验证全绿（此时 summary 文件仍在，commit-convention.md 等的 summary 引用仍有效，不报断链）
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

- [ ] **步骤 4：提交**

```bash
git add AGENTS.md template/AGENTS.md
git commit -m "refactor(agents): replace linear reading list with layering dispatch table"
```

---

### Task 2（P0）：消灭 summary 层（补 TL;DR + 清引用 + 删文件）

**目标**：4 个 full 文件补 TL;DR 承接被删 summary 的价值；清理全部剩余 summary 引用；删 4 个 summary 文件。

**文件：**

- 修改：`template/docs/ai/task-levels.md`、`branch-strategy.md`、`verification-baseline.md`、`completion-criteria.md`、`commit-convention.md`（各补 `## TL;DR` 段，3-5 行）
- 修改：`template/docs/ai/commit-convention.md`（删反向指向 `commit-convention-summary.md` 的两处链接：顶部声明行 + "提交边界摘要"链接行）
- 修改：`docs/plans/2026-08-01-ai-session-batch-and-dogfood.md`（把对 4 个 summary 的引用改指向对应 full）
- 删除：4 个 `*-summary.md`

- [ ] **步骤 1：改动前状态断言**

```bash
# 4 个 summary 文件应存在
ls template/docs/ai/{context-index,task-levels,branch-strategy,commit-convention}-summary.md  # 预期 4 个文件
# commit-convention.md 反向引用 summary
rg -c "commit-convention-summary" template/docs/ai/commit-convention.md  # 预期 ≥1
# 历史 plan 引用 summary
rg -c "summary\.md" docs/plans/2026-08-01-ai-session-batch-and-dogfood.md  # 预期 ≥4
# full 文件尚无 TL;DR 段
rg -c "^## TL;DR" template/docs/ai/task-levels.md  # 预期 0
```

- [ ] **步骤 2：4 个 full 文件补 TL;DR**

在各 full 文件标题行（`# ...`）之后、`## 目的`/`## 目标` 等首个正文段之前，插入 `## TL;DR` 段（3-5 行），内容吸收对应 summary 的高频摘要：

- `task-levels.md`：判定三问（3 问）+ 等级决策表 4 行一句话浓缩 + "AI 不得自行降级"。
- `branch-strategy.md`：四概念区分一句 + "L1+ 强制独立 worktree，不在 main 提交"。
- `verification-baseline.md`：4 档（minimal/l1/fast/full）一句话 + "verify 必跑 + 必汇报"。
- `completion-criteria.md`：五项条件一句话浓缩 + "缺验证证据视为未完成"。
- `commit-convention.md`：Conventional Commit 格式一行 + type 白名单 11 类 + "AI 不自动 commit / 不跳 hooks / 不 amend 未授权"。

> 注：`context-index.md` 不补 TL;DR（它本身是导航层，TL;DR 语义由"阅读路径"段承载）。

- [ ] **步骤 3：清理剩余 summary 引用**

1. `template/docs/ai/commit-convention.md`：删顶部声明行里"Summary 仅提供快速入口（见 commit-convention-summary.md）"及末尾"提交边界摘要：commit-convention-summary.md"链接行。
2. `docs/plans/2026-08-01-ai-session-batch-and-dogfood.md`：把对 4 个 summary 的引用改为指向对应 full 文件（`task-levels-summary.md` → `task-levels.md` 等），保持链接文本不变或更新为 full 名。

- [ ] **步骤 4：删 4 个 summary 文件**

```bash
git rm template/docs/ai/context-index-summary.md \
       template/docs/ai/task-levels-summary.md \
       template/docs/ai/branch-strategy-summary.md \
       template/docs/ai/commit-convention-summary.md
```

- [ ] **步骤 5：改动后验证**

```bash
# 4 个 summary 应已消失
ls template/docs/ai/*-summary.md 2>/dev/null  # 预期无输出
rg -c "summary\.md" --type md .  # 预期 0（全仓无 summary 引用残留）
# TL;DR 段已就位
rg -l "^## TL;DR" template/docs/ai/  # 预期命中 5 个（task-levels/branch-strategy/verification-baseline/completion-criteria/commit-convention）
# 3 条验证全绿
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0；`check-markdown-links` 报 0 broken（summary 引用已全清）。

- [ ] **步骤 6：提交**

```bash
git add template/docs/ai/task-levels.md template/docs/ai/branch-strategy.md \
       template/docs/ai/verification-baseline.md template/docs/ai/completion-criteria.md \
       template/docs/ai/commit-convention.md docs/plans/2026-08-01-ai-session-batch-and-dogfood.md
git commit -m "refactor(governance): drop summary layer, inline TL;DR into full files"
```

---

### Task 3（P0→P1 桥接）：context-index 去规则化 + 路径单一权威 + task-levels 收口门禁

**目标**：`context-index.md` 只留导航（零规则）；成为短/深路径与 Session 分流的唯一权威；`task-levels.md` 接收原 context-index 的"准入门禁"清单。两文件同一 commit，避免门禁悬空。

**文件：**

- 修改：`template/docs/ai/context-index.md`、`template/docs/ai/task-levels.md`

- [ ] **步骤 1：改动前状态断言**

```bash
# context-index.md 含规则复述段
rg -c "进入实现前准入门禁|验证入口|文档回写规则" template/docs/ai/context-index.md  # 预期 ≥3
# 全仓"3 分钟短路径"有多处定义（context-index 已是唯一 full，但确认无残留）
rg -l "3 分钟短路径" template/docs/ai/  # 预期仅 context-index.md
```

- [ ] **步骤 2：context-index.md 去规则化**

1. 删除"进入实现前准入门禁"段——把其清单内容迁移到 `task-levels.md`（步骤 3）。
2. "验证入口"段：删复述内容，改为单行链接"局部验证按 `verification-baseline.md` 的分层基线选择最窄但足够的检查"。
3. "文档回写规则"段（末尾简要复述）：删除，改为单行"详见 `doc-rewriting-rules.md`"。
4. 保留并确认"阅读路径"（短/深）、"单点定义"索引、"主要代码锚点"、"任务入口（按任务类型分流）"段——这些是导航职责。

- [ ] **步骤 3：context-index.md 成为路径唯一权威**

确认 `context-index.md` 的"阅读路径"段已吸收原 `context-index-summary.md` 的路径表述（短路径顺序、深路径落点、按 Session 分流表、Handoff 恢复路径）。原 summary 已在 Task 2 删除，本步骤确保其独有的路径表述（如"3 分钟短路径"的 5 步顺序、"按 Session 分流"表）已并入 context-index，无信息丢失。

> 校验点：`rg "3 分钟短路径" template/docs/ai/` 全仓只命中 `context-index.md` 一个文件。

- [ ] **步骤 4：task-levels.md 收口准入门禁**

在 `task-levels.md` 顶部 `## TL;DR` 之后、`## 等级矩阵` 之前，新增 `## 进入实现前准入门禁` 段，把原 context-index 的门禁清单迁入（任务级别说明、当前分支检查、分支/worktree 选择、主锚点、非目标、最小验证命令、是否需 spec/plan、spec/plan 统一落点、不得自行降级、L3 批准信号、是否需文档回写）。措辞与 task-levels 既有风格对齐。

- [ ] **步骤 5：改动后验证**

```bash
# context-index.md 规则复述段应消失（仅剩链接式指向）
rg -c "进入实现前准入门禁" template/docs/ai/context-index.md  # 预期 0
rg "验证入口|文档回写规则" template/docs/ai/context-index.md    # 预期仅剩"详见 X"链接行
# task-levels.md 收口了门禁
rg -c "进入实现前准入门禁" template/docs/ai/task-levels.md  # 预期 ≥1
# 路径唯一权威
rg -l "3 分钟短路径" template/docs/ai/  # 预期仅 context-index.md
# 3 条验证全绿
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

- [ ] **步骤 6：提交**

```bash
git add template/docs/ai/context-index.md template/docs/ai/task-levels.md
git commit -m "refactor(context-index): de-rule navigation, consolidate admission gate into task-levels"
```

---

### Task 4（P1）：governance-core ADR 降级 + 单点文件按需引用

**目标**：`governance-core.md` 删"ADR 必须与单点文件同步阅读"；单点文件对 ADR 的引用改为"有争议见 ADR-NNNN"式按需表述。

**文件：**

- 修改：`template/docs/ai/governance-core.md`、`task-levels.md`、`verification-baseline.md`、`completion-criteria.md`、`ai-role-boundaries.md`

- [ ] **步骤 1：改动前状态断言**

```bash
rg -n "同步阅读" template/docs/ai/governance-core.md  # 预期 ≥1
```

- [ ] **步骤 2：governance-core.md ADR 降级**

1. "硬约束依据（ADR）"段：把"这些 ADR 是治理基线收紧的来源，必须与单点文件同步阅读"改为"这些 ADR 是治理基线收紧的决策依据；单点文件已承载操作要求，ADR 供有争议时回溯，不必每次同步阅读"。
2. "单点文件索引"段：删指向 summary 的链接（Task 2 已删 summary，此处可能残留链接，一并清理为指向 full）。

- [ ] **步骤 3：单点文件 ADR 引用改按需**

抽查并调整以下文件中对 ADR 的引用措辞，从"详见 ADR-NNNN"（必读语气）保留为"详见"（按需），但把任何"必须先读 ADR"式表述改为"有争议时见 ADR-NNNN"：

- `task-levels.md`：L2/L3 段对 ADR-0004/0005 的引用保持"详见"（本就是按需），无需改语义，仅确认无"必须同步阅读"残留。
- `verification-baseline.md`：对 ADR-0002 的引用保持"详见"。
- `completion-criteria.md`：对 ADR-0002 的引用保持"详见"。
- `ai-role-boundaries.md`：对 ADR-0003/0005 的引用保持"详见"。

> 注：多数单点文件本就用"详见 ADR-NNNN"按需语气，本步主要是确认无"必须同步阅读"残留；真正的降级动作在 governance-core.md。

- [ ] **步骤 4：改动后验证**

```bash
rg -n "同步阅读" template/docs/ai/governance-core.md  # 预期 0
rg -n "同步阅读" template/docs/ai/                    # 预期 0（全仓无"同步阅读"残留）
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

- [ ] **步骤 5：提交**

```bash
git add template/docs/ai/governance-core.md template/docs/ai/task-levels.md \
       template/docs/ai/verification-baseline.md template/docs/ai/completion-criteria.md \
       template/docs/ai/ai-role-boundaries.md
git commit -m "refactor(governance): demote ADR from required reading to on-demand reference"
```

---

### Task 5（P1）：l2-multi-session-runbook 去重 + doc-rewriting-rules TL;DR 同步提示

**目标**：`l2-multi-session-runbook.md` 的"完成定义""verify 落点""session 序列"由复制条款改为引用 + 增量；`doc-rewriting-rules.md` 补"TL;DR 与正文同源同步"提示。

**文件：**

- 修改：`template/docs/ai/l2-multi-session-runbook.md`、`template/docs/ai/doc-rewriting-rules.md`

- [ ] **步骤 1：改动前状态断言**

```bash
# l2 runbook 应含被复制的完成定义五项 / verify 落点细则
rg -c "完成定义" template/docs/ai/runbooks/l2-multi-session-runbook.md  # 预期 ≥1
# doc-rewriting-rules 尚无 TL;DR 同步提示
rg -c "TL;DR" template/docs/ai/doc-rewriting-rules.md  # 预期 0
```

- [ ] **步骤 2：l2-multi-session-runbook.md 去重**

1. "完成定义"段：把复制的五项条件改为单行"完成定义五项条件见 `completion-criteria.md`；本 runbook 仅补充 L2 三 session 的串联纪律增量："，后接本 runbook 独有的串联纪律。
2. verify 落点细则段：把复制 ADR-0002 的核心条款改为"verify 必跑 + 必汇报的硬门禁见 `ADR-0002`；本 runbook 补充 L2 实施 session 的落点："，后接本 runbook 独有落点。
3. session 序列表：保留本 runbook 的串联视图，但删与 ADR-0003 决策表重复的字段，改为"session 数与序列的权威定义见 `ADR-0003`；本 runbook 的串联视图如下"。
4. 末尾补"## 不属于本文范围"段，声明边界（参考 `spec-and-plan-naming.md` 范式）。

- [ ] **步骤 3：doc-rewriting-rules.md 补 TL;DR 同步提示**

在"强制回写的四类场景"段中或紧随其后，补一条："单点定义文件顶部 `## TL;DR` 段与正文同源——改正文时同步更新 TL;DR，反之亦然；TL;DR 漂移视为回写缺失。"

- [ ] **步骤 4：改动后验证**

```bash
# l2 runbook 应保留引用而非复制（确认出现 completion-criteria / ADR-0002 链接）
rg -c "completion-criteria\.md|0002-verify-hard-gate" template/docs/ai/runbooks/l2-multi-session-runbook.md  # 预期 ≥2
# doc-rewriting-rules 已含 TL;DR 同步提示
rg -c "TL;DR" template/docs/ai/doc-rewriting-rules.md  # 预期 ≥1
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

- [ ] **步骤 5：提交**

```bash
git add template/docs/ai/runbooks/l2-multi-session-runbook.md template/docs/ai/doc-rewriting-rules.md
git commit -m "refactor(runbooks): replace duplicated clauses with references in l2-multi-session-runbook"
```

---

### Task 6（P2）：断链修复（CONTEXT.md 双链接歧义 + dogfood 快照水印）

**目标**：消除 `CONTEXT.md` 中 AGENTS.md 双链接歧义；为 3 个 dogfood 历史演练文件加"快照"水印。

**文件：**

- 修改：`template/docs/CONTEXT.md`、`template/docs/ai/dogfood/2026-08-ai-governance-v2-report.md`、`2026-08-batch-drill.md`、`2026-08-l2-handoff-drill.md`

- [ ] **步骤 1：改动前状态断言**

```bash
# CONTEXT.md 应含两个都指向 ../AGENTS.md 的链接但文案区分两个角色
rg -n "\.\./AGENTS\.md" template/docs/CONTEXT.md  # 预期 ≥2
# dogfood 文件应无快照水印
rg -c "快照|演练当时" template/docs/ai/dogfood/2026-08-batch-drill.md  # 预期 0
```

- [ ] **步骤 2：CONTEXT.md 消除双链接歧义**

找到文中"模板 AGENTS.md"与"仓库根 AGENTS.md"两处指向 `../AGENTS.md` 的链接。由于在 `template/docs/` 下两者都解析到 `template/AGENTS.md`，改为：保留一个链接指向 `template/AGENTS.md`，另一个改用纯文字"仓库根 AGENTS.md（采用者复制 template/AGENTS.md 后填入 Adoption Profile 的版本）"不加链接，消除"两个链接指向同文件却称两个角色"的误导。

- [ ] **步骤 3：dogfood 加快照水印**

在 3 个 dogfood 文件标题行（`# ...`）之后插入引用块：

```text
> **快照说明**：本文为演练当时（2026-08）的仓库结构快照记录。文中引用的 `.superpowers/sdd/...`、`scripts/...` 等路径可能已在后续重构（见 `2026-08-02-template-restructure`）中调整；本文保留原样作为历史记录，不作为当前路径权威。
```

- [ ] **步骤 4：改动后验证**

```bash
rg -n "\.\./AGENTS\.md" template/docs/CONTEXT.md  # 预期 ≤1（双链接已收敛）
rg -c "快照|演练当时" template/docs/ai/dogfood/2026-08-batch-drill.md        # 预期 ≥1
rg -c "快照|演练当时" template/docs/ai/dogfood/2026-08-l2-handoff-drill.md  # 预期 ≥1
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

- [ ] **步骤 5：提交**

```bash
git add template/docs/CONTEXT.md template/docs/ai/dogfood/
git commit -m "docs: fix CONTEXT.md dual-link ambiguity and add snapshot watermark to dogfood drills"
```

---

### Task 7（P2）：新增 ADR-0006

**目标**：新增 ADR 记录本次收敛作为长期决策依据；更新 ADR 索引。

**文件：**

- 新建：`template/docs/adr/0006-reading-path-layering.md`
- 修改：`template/docs/adr/README.md`

- [ ] **步骤 1：改动前状态断言**

```bash
ls template/docs/adr/0006-*.md 2>/dev/null  # 预期无输出（尚未创建）
rg -c "0006" template/docs/adr/README.md   # 预期 0
```

- [ ] **步骤 2：新建 ADR-0006**

按 `adr/adr-template.md` 骨架创建 `template/docs/adr/0006-reading-path-layering.md`，状态 `Accepted`。内容要点：

- **决策**：AI 阅读路径采用四层分离（边界/导航/规则/依据/模板）+ 分流入口，取代线性通读 11 链。
- **背景**：诊断发现三套入口打架、summary 层冗余（入度 2/3/3/3、标题=full 子集）、通读过载（1403 行）、导航复述规则、ADR 当操作手册。
- **决策依据**：导航/规则/依据/模板各层单一权威；按需取代通读；删 summary、价值下沉为 full TL;DR。
- **后果**：L0 必读量 ~1400→~250 行；ADR 降为按需回溯（硬约束操作面已落单点文件）；新增 full 顶部 TL;DR 维护义务（见 doc-rewriting-rules）。
- **修订记录**：初版 2026-08-09。
- **关联**：ADR-0003（多 session，不改其结论）、ADR-0004（spec/plan 分离，不改其结论）。

- [ ] **步骤 3：更新 ADR 索引**

在 `template/docs/adr/README.md` 索引表补一行 ADR-0006。

- [ ] **步骤 4：改动后验证**

```bash
ls template/docs/adr/0006-reading-path-layering.md  # 预期文件存在
rg -c "0006" template/docs/adr/README.md             # 预期 ≥1
# ADR 状态校验（doctor 检查 0002-0005 非 Proposed，0006 应为 Accepted 不触发 fail）
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

> 校验点：确认 `check-governance-consistency.py` 不会因新增 ADR-0006 而报"未引用"或"状态非法"。若脚本对 ADR 编号有连续性断言（如要求 0006 必须被某文件引用），在此 Task 补引用。

- [ ] **步骤 5：提交**

```bash
git add template/docs/adr/0006-reading-path-layering.md template/docs/adr/README.md
git commit -m "docs(adr): add ADR-0006 reading path four-layer separation"
```

---

## 全 Task 收尾验证

所有 Task 完成后，从 worktree 根跑一次完整验证，并核对 spec 验收标准：

- [ ] **步骤 1：跑 3 条验证**

```bash
bash template/scripts/scaffold-doctor.sh --template
python3 template/scripts/check-markdown-links.py --root . --template
python3 template/scripts/check-governance-consistency.py --root . --template
```

预期：全部退出码 0。

- [ ] **步骤 2：核对 spec 验收标准（抽样）**

```bash
# 结构层：4 个 summary 消失
ls template/docs/ai/*-summary.md 2>/dev/null  # 预期无输出
# 入口层：AGENTS 无通读清单 + 有分流表
rg -c "按以下顺序阅读" AGENTS.md template/AGENTS.md  # 预期 0 0
rg -c "## 分流入口" AGENTS.md template/AGENTS.md    # 预期 1 1
# 导航层：context-index 无规则复述
rg -c "进入实现前准入门禁" template/docs/ai/context-index.md  # 预期 0
# ADR 层：governance 无"同步阅读"
rg -c "同步阅读" template/docs/ai/governance-core.md  # 预期 0
# 一致性：路径唯一权威
rg -l "3 分钟短路径" template/docs/ai/  # 预期仅 context-index.md
# 阅读量：L0 必读集行数
wc -l AGENTS.md template/docs/ai/context-index.md  # 对照 ≤250 行目标（人工判断）
```

- [ ] **步骤 3：把最终验证结果填入下方 `## 验证证据` 表**

## 批准（L3 任务必填，其他任务留空）

> 本任务为 L2，本段非必填（详见 [ADR-0005](../../template/docs/adr/0005-l3-approval-gate.md)）。spec 已由用户"确认 spec，继续 plan"信号确认；plan 进入实施 session 不需 L3 批准门禁。

## 验证证据（实施 session 末尾必填）

> 本表由**实施 session**在跑完验证后填写；规划 session 不允许填写，仅交付 spec + plan 双份。

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| (基线)`bash template/scripts/scaffold-doctor.sh --template` | | | Task 0 基线 |
| (基线)`python3 template/scripts/check-markdown-links.py --root . --template` | | | Task 0 基线 |
| (基线)`python3 template/scripts/check-governance-consistency.py --root . --template` | | | Task 0 基线 |
| (Task 1 后)`bash template/scripts/scaffold-doctor.sh --template` | | | |
| (Task 2 后)`python3 template/scripts/check-markdown-links.py --root . --template` | | | summary 删除后无断链 |
| (Task 7 后 / 最终)`bash template/scripts/scaffold-doctor.sh --template` | | | |
| (最终)`python3 template/scripts/check-governance-consistency.py --root . --template` | | | |

未跑项：

## Session Handoff

- Task Level: L2
- Current Phase: 规划完成（spec 已确认 + plan 草稿产出），待进入实施 session
- Status: blocked（等待用户批准进入实施 session 的信号）
- Completed: spec 确认；plan 8 个 Task 切片产出；baseline 验证全绿；summary 引用依赖摸清（根 AGENTS + template AGENTS + 历史 plan batch-and-dogfood + commit-convention 反向引用）
- Artifacts: `docs/specs/2026-08-09-ai-reading-path-restructure.md`、`docs/plans/2026-08-09-ai-reading-path-restructure.md`（本文件）
- Decisions: TL;DR 用 `## TL;DR` 二级标题（spec Open Q1 默认）；分流表只按 L 级别分流，session 角色分流交 context-index（spec Open Q2 默认）；Task 顺序"先重构 AGENTS.md 移除引用 → 再删 summary"，保证每 Task 末尾无断链；Task 3 合并 context-index 去规则化与 task-levels 收口门禁于同一 commit，避免门禁悬空
- Assumptions: 4 个 full 补 TL;DR 能覆盖原 summary 的快速浏览价值；`check-governance-consistency.py` 不硬编码 summary 路径（已验证，删除安全）；新增 ADR-0006 不会触发 governance 一致性 fail（Task 7 步骤 4 有兜底校验）
- Open Questions: TL;DR 段是否需要在 `spec-and-plan-naming.md` 或模板里正式约束为必填？（本 plan 仅作为习惯引入，未升为硬约束——评审 session 决定是否回写为规则）
- Verification: plan 为规划产物，未跑实施验证；baseline（Task 0 前置）已跑通 0 fail / 0 warning
- Next Allowed Actions: 用户批准进入实施 session 后 → 按 Task 1→7 顺序执行 → 每 Task 末尾 commit + 验证全绿 → 收尾跑全 Task 验证 + 核对 spec 验收标准 → 填 `## 验证证据` 表 → 进入评审 session
- Prohibited Scope: 实施 session 不得改任何治理文件的规则语义；不得改 Adoption Profile 10 字段；不得改模板骨架字段；不得引入新机制；不得在 main 提交；不得跳过任一 Task 的"改动后验证"步骤
