# 重构 AI 阅读路径：四层分离 + 分流入口

> L2 设计 spec。L2 任务必须先按本 spec 产出 `docs/specs/<date>-<name>.md`，用户确认后再按 [implementation-plan.md](../../template/docs/ai/templates/implementation-plan.md) 模板产出 `docs/plans/<date>-<name>.md`；spec 与 plan 是两份独立文件（详见 [ADR-0003](../../template/docs/adr/0003-multi-session-l2.md) 与 [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md)）。
>
> **本 spec 不写执行切片**——任务切片、步骤、命令、文件清单、回滚路径属于 plan，不在本文件范围（详见 [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md) 的"spec 与 plan 最小接口"段）。本 spec 只描述"目标行为状态"与"外部可判据"，具体改哪些文件、按什么顺序改、每步跑什么命令，由 plan 承接。

## 元信息

- 主题：reading-path, layering, navigation, governance, dedup
- 状态：`draft`
- 关联 ADR：沿用 [ADR-0002](../../template/docs/adr/0002-verify-hard-gate.md) / [ADR-0003](../../template/docs/adr/0003-multi-session-l2.md) / [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md)；建议实施阶段新增 ADR-0006 记录本次收敛

## 背景

本仓库作为 AI 驱动开发治理脚手架，`AGENTS.md` 顶部"治理入口"段要求 AI"按以下顺序阅读"11 个文件。诊断发现当前 AI 阅读路径存在六类问题，已用证据量化：

### 问题 1：入口路径存在三套互相打架的"权威"

同一个"AI 该按什么顺序读"的问题，仓库给出三个不一致的答案：

| 出处 | 它宣称的第一站 |
|---|---|
| `AGENTS.md` 治理入口 | context-index-summary → governance-core → task-levels-summary…（11 链线性通读）|
| `context-index-summary` 的"3 分钟短路径" | AGENTS.md → task-levels-summary → branch-strategy-summary → CONTEXT |
| `context-index.md` 的"短路径" | AGENTS.md → context-index.md（自己）→ CONTEXT → 任务入口 |

三者的第 2、3 站全不一样。`context-index.md` 自己已察觉并就地打补丁（"该含义与 template 原文有出入，本节以本节为准"）——这是路径漂移的现场证据。

### 问题 2：summary 层 ROI 极低，且与 full 严重冗余

| summary | full | 共同行 | summary 独有增量 | summary 入度 |
|---|---|---|---|---|
| context-index-summary(63行) | context-index(136行) | 25 | 38 | **2** |
| task-levels-summary(57行) | task-levels(137行) | 28 | 29 | **3** |
| branch-strategy-summary(76行) | branch-strategy(126行) | 41 | 35 | **3** |
| commit-convention-summary(36行) | commit-convention(175行) | 22 | 15 | **3** |

标题树对比更直白：4 组 summary 的小节标题几乎是 full 标题的**子集**（branch-strategy 两组各 8 节几乎一一对应）。同时这 4 个 summary 是全文档图入度最低的节点（2/3/3/3），却被摆在"第一入口"位置——占阅读量却无人回引。`commit-convention.md` 还反向指回 summary，形成双向引用。`context-index-summary` 名为"快速摘要"，却塞进"深路径 L2/L3""按 Session 分流表""Handoff 11 字段"——与 `context-index.md` 抢职责，制造第二个漂移源。

### 问题 3："治理入口"被设计成线性通读，违反按需原则

`AGENTS.md` 治理入口要求按顺序读 11 个文件，光入口层即 **1403 行**，其中大量触发型规则被当成必读：

- `commit-convention`（要提交才读）→ 列为第 7 站必读
- `ai-role-boundaries`（L2+ 多 session 才读）→ 列为第 8 站必读
- `doc-rewriting-rules`（触及长期约定才读）→ 列为第 9 站必读

这违背 summary 自己承诺的"3 分钟短路径"——AI 为判断走哪条路，得先读完 1400 行导航。

### 问题 4：导航/规则分离不彻底：导航文件复述规则

`context-index.md` 一边声明"只聚合入口和判断顺序，不替代 spec/plan/runbook"，一边塞了"进入实现前准入门禁""验证入口""文档回写规则简要复述"——这些是规则内容，本应只在 `task-levels.md` / `verification-baseline.md` / `doc-rewriting-rules.md` 出现。导航文件复述规则 = 第二个权威源，必然漂移。`AGENTS.md` 底部"任务入口速查表"与 `context-index.md` 的"任务入口（按任务类型分流）"表也高度重叠，把导航层的活抢了一半。

### 问题 5：ADR 被当操作手册用，而非决策依据

`governance-core` 要求"ADR 必须与单点文件同步阅读"。但 ADR 是 **why**（决策依据），单点文件是 **what/how**。绝大多数场景只需单点文件 + runbook；ADR 应是"有争议时回溯"的按需文档，不该进必读链。

### 问题 6：外围层重复与断链

- **重复最严重**：`l2-multi-session-runbook.md` 大段复制 `completion-criteria` 五项条件、`ADR-0002` verify 条款、`ADR-0003` session 序列——每次治理修订都要手动同步。
- **断链**：`CONTEXT.md` 里"模板 AGENTS.md"和"仓库根 AGENTS.md"两个链接在 `template/docs/` 下都解析到同一文件，文案却区分两个角色；`dogfood/2026-08-*.md` 引用的 `.superpowers/sdd/...` 与 `scripts/...` 路径已不存在（历史演练，应加"快照"水印）。

### 为什么现在启动

本仓库在 [GOV 收敛](../plans/2026-08-01-ai-governance-rule-convergence.md) 之后，治理文档数量趋于稳定；上一轮 L2（`2026-08-02-template-restructure`）已把下发物物理收拢到 `template/`，目录语义已清晰。现在适合做"阅读路径"层的收敛——把"导航""规则""决策依据""执行模板"在路径上彻底分离，后续任何新增单点定义/runbook 都能直接落在正确的层，避免再出现"该进必读链还是按需"的两难。

## 目标

把 AI 阅读路径从"线性通读 11 链"重构为"四层分离 + 分流入口"，使每层只干一件事；L0 新会话的必读量从 ~1400 行压到 ~200 行，且导航/规则/依据/模板各层单一权威、不再有第二份易漂移的摘要源。

## 行为

### 四层分离模型（重构后状态）

重构后，仓库文档按职责分四层，读取时机不同：

| 层 | 职责 | 文件 | 读取时机 |
|---|---|---|---|
| **L0 边界层** | 不可破坏的硬边界 + 分流入口（决策表） | `AGENTS.md` | 每次必读 |
| **L1 导航层** | 判断顺序 + 跳转链接，**零规则内容** | `context-index.md`（合并后唯一） | 每次必读 |
| **L2 规则层** | 单点定义，每文件顶部带 3–5 行 TL;DR | task-levels / branch-strategy / verification-baseline / completion-criteria / ai-role-boundaries / doc-rewriting-rules / commit-convention | **按级触发** |
| **L3 依据层** | 决策 why，不当操作手册 | ADR-0001~0005 | **有争议才回溯** |
| **L4 模板层** | runbook / template / checklist | 按工作流选 | **走对应流程才读** |

关键转变：L2 规则层、L3 依据层、L4 模板层全部从"必读链"降为"触发型按需"。

### 分流入口（AGENTS.md 末尾唯一权威）

重构后 `AGENTS.md` 末尾只保留一张分流决策表。AI 读 `AGENTS.md` 后，回答"我是什么级别"（L0–L3，用 task-levels 的判定三问）即可拿到本次精确必读集：

| 改动级别 | 本次必读集 | 触发型（发生才读）|
|---|---|---|
| L0 | AGENTS + context-index + task-levels + 代码锚点 | commit-convention（要提交时）|
| L1 | + task-packet + branch-strategy + verification-baseline | doc-rewriting-rules（触及长期约定时）|
| L2 | + 对应 runbook + spec/plan 模板 + ai-role-boundaries + completion-criteria | ADR-0003/0004（有争议时）|
| L3 | + ADR-0005 + 对应 brief | ADR-0001/0002（有争议时）|

此表是**唯一的入口权威**，其余文件只链接不复述。

### summary 层消失

4 个 `*-summary.md` 文件（context-index-summary / task-levels-summary / branch-strategy-summary / commit-convention-summary）从仓库物理删除。其"快速浏览"价值下沉为对应 full 文件顶部一段 3–5 行 TL;DR（吸收判定三问、等级决策表、type 白名单等高频摘要）。`commit-convention.md` 删掉反向指向 summary 的链接，双向引用随之消失。

### 导航层去规则化

`context-index.md` 只保留"短/深路径判断 + 跳转链接 + 代码锚点占位 + 按任务类型分流表"，移除以下三段（迁回单点文件）：

- "进入实现前准入门禁" → 并入 `task-levels.md` 各级定义（P1 完成）
- "验证入口" → 由 `verification-baseline.md` 承载，导航只指向它
- "文档回写规则简要复述" → 删除，由 `doc-rewriting-rules.md` 承载

`context-index-summary` 与 `context-index.md` 的路径表述合并为 `context-index.md` 一处权威；`AGENTS.md` 治理入口段与"任务入口速查表""文档分层速记"删除（这些是导航层的活）。

### ADR 降级为按需回溯

`governance-core.md` 删除"ADR 必须与单点文件同步阅读"要求；改为单点文件内"有争议见 ADR-NNNN"式按需引用。硬约束的**操作要求**已落在单点文件与 runbook（如 verify 必跑写在 verification-baseline + completion-criteria），ADR 只留"为什么这么定"。

### 外围层去重

- `l2-multi-session-runbook.md`：完成定义、verify 落点细则、session 序列由"复制条款"改为"引用 + 增量"（引用 completion-criteria / ADR-0002 / ADR-0003，只保留本 runbook 独有的串联纪律）。
- 推广 `spec-and-plan-naming.md` 已有的"显式声明边界、不重复"范式，为去重后的外围文件补"不属于本文范围"段。

### 断链修复

- `CONTEXT.md`：改"模板 AGENTS.md"与"仓库根 AGENTS.md"文案，消除同文件双链接歧义。
- `dogfood/2026-08-*.md`：在文件首加"路径为演练当时快照，当前结构可能已重构"水印，不改正文。

### 新增 ADR

新增 [ADR-0006](../../template/docs/adr/) 记录本次收敛（四层分离、删 summary、ADR 降级、分流入口）作为长期决策依据；与 ADR-0003（多 session）、ADR-0004（spec/plan 分离）并列，但**不**改写它们的结论。

## 非目标

- **不动治理语义**——任务分级的判定条件、验证基线档位语义、提交规范实质规则、ADR 的决策结论全部不变；本次只动"它们被如何被 AI 找到与读取"，不动它们说了什么。
- **不改 Adoption Profile 10 字段**——`AGENTS.md` 顶部"用户项目元信息"段的 10 个字段（含 4 个验证入口、Isolation Profile）保持不变。
- **不改外围 runbook 的"增量内容"**——只改它们的"复制→引用"重复部分；feature/bugfix/refactor-delivery-runbook 各自独有的工作流差异内容不动。
- **不引入新机制**——不新增 CI 门禁、不新增 doctor 检查器、不新增 bootstrap 脚本、不改 `worktree-add.sh`。
- **不解决 worktree prefix 分隔符分歧**（slash vs hyphen，见 `worktree-add.sh` 顶部注释），沿用现状。
- **不重写 dogfood 历史报告正文**——只加"快照"水印。
- **不动 `task-packet.md` / `feature-spec.md` / `implementation-plan.md` 等模板的结构**——它们是采用者会复制的下发物，模板字段不动；只可能在 plan 里微调引用路径，不改模板骨架。
- **不强行统一"短路径/深路径"的措辞风格**——只保证**单一文件定义**，措辞保留各文件原有风格。
- **不解决 `batch-ai-execution-runbook` 引用 `completion-criteria` "批量集成条件"段的逻辑**（侦察曾误报为断链，实际 `completion-criteria.md` 已含该段标题，非真断链；本次不动这条）。

## 验收（外部可判据）

每条以"满足 X 即验收"形式给出，可被外部独立判断。

### 结构层

- `template/docs/ai/` 下不再存在 `context-index-summary.md`、`task-levels-summary.md`、`branch-strategy-summary.md`、`commit-convention-summary.md` 四个文件（`fd` 查无结果）。
- 4 个对应 full 文件（context-index / task-levels / branch-strategy / commit-convention）顶部各有一段 TL;DR（以 `## TL;DR` 或等价前置段形式存在，3–5 行）。

### 入口层

- `AGENTS.md` 不再含"治理入口"段的 11 链通读清单（`rg -n "按以下顺序阅读"` 在 AGENTS.md 无命中）。
- `AGENTS.md` 末尾含且仅含一张分流决策表（L0/L1/L2/L3 × 必读集 × 触发型），作为入口唯一权威。
- `AGENTS.md` 不再含"任务入口速查"表与"文档分层速记"表（这两项职责归导航层）。

### 导航层

- `context-index.md` 不再含"进入实现前准入门禁""验证入口""文档回写规则简要复述"三段（`rg -n "准入门禁|验证入口|简要复述"` 在该文件无命中，或命中处已改为"详见 X"的纯链接）。
- 仓库内**有且仅有一处**定义"3 分钟短路径"与"深路径"的阅读顺序（`rg -l "3 分钟短路径"` 全仓仅命中 `context-index.md` 一个文件）。

### ADR 层

- `governance-core.md` 不再含"ADR 必须与单点文件同步阅读"表述（`rg -n "同步阅读"` 在该文件无命中）。
- 单点文件内对 ADR 的引用改为"有争议见 ADR-NNNN"式按需表述（抽查 task-levels / verification-baseline / completion-criteria 三处）。

### 一致性层

- 全仓不存在第二个"短/深路径"或"Session 分流"的定义源（除 `context-index.md` 与 `session-handoff-protocol.md` 各管一段外，无文件复述）。
- `commit-convention.md` 不再反向指向 `commit-convention-summary.md`（该 summary 已删除）。

### 工具层（退出码 0）

以下命令在 repo 根执行，均退出码 0：

- `bash template/scripts/scaffold-doctor.sh --template`
- `python3 template/scripts/check-markdown-links.py --root . --template`
- `python3 template/scripts/check-governance-consistency.py --root . --template`

### 阅读量层

- L0 必读集（AGENTS.md + context-index.md + task-levels.md 的 TL;DR + 锚点段）总行数 ≤ 250 行（重构前入口层 1403 行）。

## 范围级别

- **建议任务级别**：`L2`
- **为什么适用这个级别**：
  - 跨多个治理文件的路径权威重构，涉及 4 个文件删除、`AGENTS.md` 入口段重写、`context-index.md` 去规则化、`governance-core.md` ADR 定位调整、4 个 full 文件补 TL;DR、1 个外围 runbook 去重、1 个新 ADR。
  - 影响"入口"（AGENTS.md 治理入口、context-index 导航）与"数据流"（链接解析网络），符合 L2 在 [task-levels.md](../../template/docs/ai/task-levels.md) 中的定义。
  - 不触及鉴权、依赖、CI 策略、安全，不需要 L3 批准门禁。

## 受影响边界

- **物理布局**：`template/docs/ai/` 下 4 个 `*-summary.md` 文件删除。
- **路径引用**：`AGENTS.md`（治理入口段、任务速查表、文档分层速记段）；`context-index.md`（准入门禁/验证入口/回写规则三段）；`governance-core.md`（ADR 同步阅读要求、单点文件索引中 summary 链接）；4 个 full 文件（补 TL;DR）；`l2-multi-session-runbook.md`（去重段）；`CONTEXT.md`（双链接歧义）；`dogfood/2026-08-*.md`（水印）。
- **导航语义**：入口路径权威从"三处"收敛为"一处"（`context-index.md`）；分流入口表成为 `AGENTS.md` 末尾唯一入口权威。
- **决策依据层**：`governance-core.md` 与单点文件对 ADR 的引用方式从"必读"降为"按需回溯"。
- **工具链**：无脚本改动；`check-markdown-links.py` 与 `check-governance-consistency.py` 须在删除 summary 后仍通过（summary 被引用处需同步清理）。

## 建议方案

**四层分离 + 分流入口**（见"行为"段）。它符合当前仓库既有模式——`spec-and-plan-naming.md` 已经是"显式声明边界、不重复"的范例，本方案把这一范式从"单个文件"推广到"整层"；`ADR-0002` 已经把"verify 必跑"作为硬约束落在操作层而非 ADR 层，本方案把同样的思路推广到"ADR 整体降级为按需回溯"。

切片建议按 P0 → P1 → P2 推进（详见 plan，本 spec 不写切片）：

- **P0（收益最大）**：删 summary 层 + `AGENTS.md` 入口重构 + `context-index.md` 去规则化 + 三套路径收敛为单一权威。
- **P1**：`task-levels` 收口准入门禁 + ADR 降级 + `l2-multi-session-runbook` 去重。
- **P2**：断链修复（CONTEXT.md、dogfood 水印）+ 新增 ADR-0006。

## 备选方案

### 方案 A：保留 summary 层，但改造为"纯导航卡片"

不删 4 个 summary，而是把它们改造成只含"何时读我 + 一句话定位 + 跳转链接"的卡片，禁止承载规则内容。

**为什么不采用**：标题树已证明 summary 的小节标题 = full 标题子集，说明它们没有 full 之外的独立信息架构；改造为"纯卡片"后，卡片的内容（何时读我、一句话定位）恰恰应该就是 full 顶部 TL;DR 的内容——保留 summary 等于维护一份与 TL;DR 重复的卡片，仍需双向同步。删 summary + full 补 TL;DR 更简单（少一个文件、少一处漂移源），符合"最少代码解决问题"。

### 方案 B：保留线性通读，只在通读清单上标注"按需"

不动结构，只在 `AGENTS.md` 治理入口的 11 链上给每条加"必读/按需"标签，让 AI 自行跳过按需项。

**为什么不采用**：这只解决了问题 3（通读过载），没解决问题 1（三套打架）、问题 2（summary 冗余）、问题 4（导航/规则混淆）、问题 5（ADR 当手册）。而且"让 AI 自行跳过按需项"把判断负担推给 AI，不如用分流表直接给出"本次必读集"确定性高。方案 B 是在旧结构上打补丁，本方案是收敛结构本身。

## 验证计划（仅策略层）

> 具体命令与退出码属 plan 的 `## 验证证据` 段，本段只写策略。

- **结构回归**：删除 summary 后，全仓无断链（`check-markdown-links.py`）、治理一致性通过（`check-governance-consistency.py`）、doctor 通过（`scaffold-doctor.sh --template`）。这覆盖"删 summary 是否留下悬空引用"这一主回归风险。
- **主用户流程（L0 新会话模拟）**：以 L0 视角只读"AGENTS.md + context-index + task-levels TL;DR + 锚点"，验证能否独立判断"我该走哪条路、本次必读哪些、要提交时再读 commit-convention"——分流表的可达性与自洽性。
- **一致性检查**：`rg` 验证"3 分钟短路径"等关键表述全仓唯一命中 `context-index.md`，确认无第二权威源残留。
- **阅读量核验**：统计 L0 必读集行数 ≤ 250 行。
- **无需 e2e**：本次为纯文档结构重构，无运行时行为，doctor + link check + governance consistency 已是端到端覆盖。

## 风险

- **行为回归风险**：删除 summary 后，若某文件仍引用已删 summary，产生断链。缓解：P0 删除前先 `rg` 全仓扫描 summary 引用，逐一改为指向 full；plan 切片把"扫描+清理"作为删 summary 的前置步。
- **边界漂移风险**：full 文件顶部新增的 TL;DR 与正文不同步（后续改正文忘改 TL;DR）。缓解：TL;DR 只放"判定三问/等级决策表"等极稳定的高频摘要，不放易变细节；并在 `doc-rewriting-rules.md` 补一条"TL;DR 与正文同源同步"的回写提示（属 P1）。
- **导航去规则化后的遗漏风险**：`context-index.md` 移除"准入门禁"后，若 `task-levels.md` 未同步收口，AI 可能漏掉门禁。缓解：P1 把"准入门禁"清单迁入 `task-levels.md` 各级定义，作为 P0 的紧后切片，二者不能跨 session 间隔。
- **分流表与实际按需集不匹配风险**：分流表给出的"本次必读集"若遗漏某 L 级实际需要的文件，AI 会少读。缓解：plan 评审 session 用各 L 级历史 spec/plan 做对照抽样，核对分流表覆盖。
- **ADR 降级后的硬约束遗漏风险**：AI 误以为"ADR 不必读 = ADR 约束可忽略"。缓解：分流表 L3 行仍把 ADR-0005 列入必读，且单点文件内"有争议见 ADR-NNNN"的引用保留 ADR 作为回溯入口；硬约束的操作面已落在单点文件，不依赖 AI 读 ADR。

## 需要更新的文档

- `AGENTS.md`：治理入口段重写为分流表；删任务速查表与文档分层速记段。
- `template/docs/ai/context-index.md`：去规则化；成为短/深路径与 Session 分流的唯一权威。
- `template/docs/ai/governance-core.md`：ADR 定位从"同步阅读"降为"按需回溯"；单点文件索引删 summary 链接。
- `template/docs/ai/task-levels.md`：补 TL;DR；P1 收口"准入门禁"。
- `template/docs/ai/branch-strategy.md` / `verification-baseline.md` / `completion-criteria.md` / `commit-convention.md`：各补 TL;DR；删 summary 反向引用。
- `template/docs/ai/l2-multi-session-runbook.md`：去重段改"复制→引用 + 增量"。
- `template/docs/CONTEXT.md`：消除 AGENTS.md 双链接歧义。
- `template/docs/ai/dogfood/2026-08-*.md`：加快照水印。
- `template/docs/adr/`：新增 ADR-0006（本次收敛依据）。
- `template/docs/ai/doc-rewriting-rules.md`：补"TL;DR 与正文同源同步"提示（P1）。

## Session Handoff

> L2 规划 Session 结束后，本段流转到 plan 末尾 `## Session Handoff` 承接；按 [session-handoff-protocol.md](../../template/docs/ai/runbooks/session-handoff-protocol.md) 填写 11 个必填字段。本 spec 当前为状态入口。

- Task Level: L2
- Current Phase: 规划（spec 草稿，待用户确认）
- Status: blocked（等待用户对 spec 的确认信号）
- Completed: AI 阅读路径诊断完成（三套入口打架 / summary 冗余 / 通读过载 / 导航规则混淆 / ADR 当手册 / 外围层重复断链，均已量化）；四层分离 + 分流入口方案设计完成；spec 草稿产出
- Artifacts: `docs/specs/2026-08-09-ai-reading-path-restructure.md`（本文件）
- Decisions: 采用四层分离 + 分流入口，而非保留 summary 改造（方案 A）或线性通读加按需标签（方案 B）；summary 价值下沉为 full 顶部 TL;DR；ADR 整体降级为按需回溯
- Assumptions: 4 个 full 文件补 TL;DR 后能覆盖原 summary 的快速浏览价值；`task-levels.md` 能完整收口原 context-index 的准入门禁清单
- Open Questions: TL;DR 段的统一标题用 `## TL;DR` 还是 `> **TL;DR**` 引用块？分流表是否需要补"评审 session"行（当前只按 L 级别分流，未按 session 角色分流）？
- Verification: 本 spec 为设计文档，未跑实施验证；baseline `scaffold-doctor.sh --template` 已在 worktree 建立时跑通（0 fail / 0 warning）
- Next Allowed Actions: 用户确认 spec 后 → 写 plan（按 P0/P1/P2 切片）→ 进入实施 session
- Prohibited Scope: 不得在本 spec 阶段改任何治理文件正文；不得在用户确认前写 plan；不得自行降级为 L1 直接实施

## 批准

> L2 任务本段非必填（详见 [ADR-0005](../../template/docs/adr/0005-l3-approval-gate.md)）。本 spec 等待用户"确认 spec"信号后流转到 plan，不涉及 L3 批准门禁。

## 验证证据（实施 session 末尾必填）

> 本表由**实施 session**在跑完验证后填写；规划 session 不允许填写，仅交付 spec + plan 双份。

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| (基线)`bash template/scripts/scaffold-doctor.sh --template` | 0 | Summary: 0 fail(s), 0 warning(s) | Task 0 基线 |
| (基线)`python3 template/scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | Task 0 基线 |
| (基线)`python3 template/scripts/check-governance-consistency.py --root . --template` | 0 | clean | Task 0 基线 |
| (Task 1 后)`bash template/scripts/scaffold-doctor.sh --template` | 0 | 0 fail / 0 warning | AGENTS 入口重构（删 11 链 + 分流表）后 |
| (Task 2 后)`python3 template/scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | 4 summary 删除后无断链（历史 plan 的 summary 引用为反引号纯路径，非链接） |
| (Task 7 后 / 最终)`bash template/scripts/scaffold-doctor.sh --template` | 0 | 0 fail / 0 warning | 全 Task 完成 |
| (最终)`python3 template/scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | 全 Task 完成 |
| (最终)`python3 template/scripts/check-governance-consistency.py --root . --template` | 0 | clean | 全 Task 完成 |

未跑项：无（doctor / link / governance 三档每 Task 末尾均跑，全退出码 0）
