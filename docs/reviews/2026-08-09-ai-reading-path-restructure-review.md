# Review Report：AI 阅读路径重构（四层分离 + 分流入口）

> 评审 session 交付物。按 [review-checklist.md](../../template/docs/ai/checklists/review-checklist.md) 结构独立核对。
> **评审独立性声明**（[ADR-0003](../../template/docs/adr/0003-multi-session-l2.md)）：本 session 从零上下文进入，**未读**实施 session 的中间对话；所有判定基于 `git diff main..HEAD` + spec/plan 物理文件 + 本 session 复跑验证。交接文档 `/tmp/handoff-reading-path-review-2026-08-09.md` 仅作"实施者自陈 + 入口索引"，其结论不被采信为既定事实。
> 回链 plan：[docs/plans/2026-08-09-ai-reading-path-restructure.md](../plans/2026-08-09-ai-reading-path-restructure.md)；spec：[docs/specs/2026-08-09-ai-reading-path-restructure.md](../specs/2026-08-09-ai-reading-path-restructure.md)

## 评审范围与基线

- 分支：`refactor-ai-reading-path`（worktree `.worktrees/refactor-ai-reading-path`）
- 基线：`main`（33aeb3b）；本分支领先 9 commit
- 任务等级：L2（spec/plan 双份，三 session 串行：规划 ✓ → 实施 ✓ → 评审（本次））

## 结论（TL;DR）

**判定：返工（request changes）**——存在 1 个阻塞项。

| 级别 | 项 | 一句话 |
|---|---|---|
| 🔴 Blocking | B1 | spec 的 `## 验证证据` 段未填（空表），违反"spec/plan 双份必填"硬门禁 |
| 🟡 Minor | M1 | 6/9 commit subject > 72 字符 |
| 🟡 Minor | M3 | context-index 残留 stale"本节以本节为准"补丁注 |
| ⚪ Nit | O1 | spec+plan 同一 commit（边界 checklist 严格读可视为混合） |
| ⚪ Nit | O2 | review-checklist 列"plan 必含回滚"但 implementation-plan 模板无回滚 slot（治理文档自身不一致，非 plan 缺陷） |

阻塞项补填后重跑验证即可进合并决策；M1/M3/O1/O2 为非阻塞 follow-up。

---

## 复跑验证证据（本 session fresh run）

按 [verification-before-completion](#) 纪律，本 session 重新执行全部验证命令，不采信 plan 自填结论。

| 命令 | 退出码 | 关键输出 | 与 plan 自填是否一致 |
|---|---|---|---|
| `bash template/scripts/scaffold-doctor.sh --template` | 0 | `Summary: 0 fail(s), 0 warning(s)` | 一致 |
| `python3 template/scripts/check-markdown-links.py --root . --template` | 0 | 0 broken | 一致 |
| `python3 template/scripts/check-governance-consistency.py --root . --template` | 0 | clean | 一致 |
| `python3 template/scripts/check-spec-and-plan-naming.py` | 0 | clean | 一致 |
| `git status --porcelain` | — | 空（worktree 干净，全已提交） | 一致 |

> 4 条全 0，与 plan `## 验证证据` 表自填一致。**但 plan 自填的 verify 证据仅落 plan 一份，spec 末尾同名段仍空**——见 B1。

## spec 验收标准独立复核

逐条对照 spec `## 验收` 段，本 session 用 `rg`/`ls` 实跑：

| 验收条目 | 命令 | 实跑结果 | 判定 |
|---|---|---|---|
| 结构层：4 summary 物理删除 | `ls template/docs/ai/*-summary.md` | 无输出 | ✓ |
| 结构层：full 顶部有 TL;DR | `rg -l "^## TL;DR" template/docs/ai/` | 命中 5（task-levels/branch-strategy/verification-baseline/completion-criteria/commit-convention）；context-index 用"阅读路径"等价前置段（spec 验收允许"等价前置段形式"） | ✓（见 O2 偏差记录） |
| 入口层：AGENTS 无通读清单 | `rg -c "按以下顺序阅读" AGENTS.md template/AGENTS.md` | 0 | ✓ |
| 入口层：AGENTS 有分流表 | `rg -c "## 分流入口" AGENTS.md template/AGENTS.md` | 各 1 | ✓ |
| 入口层：无任务速查/分层速记 | `rg -c "任务入口速查\|文档分层速记"` | 0 | ✓ |
| 导航层：context-index 无准入门禁 | `rg -c "进入实现前准入门禁" context-index.md` | 0（已迁 task-levels，task-levels 命中 1） | ✓ |
| 导航层：3 分钟短路径唯一权威 | `rg -l "3 分钟短路径" template/docs/ai/` | 仅 context-index.md | ✓ |
| ADR 层：governance 无"同步阅读" | `rg -c "同步阅读" governance-core.md` | 0 | ✓ |
| 一致性：commit-convention 无反向指 summary | `rg -c "commit-convention-summary" commit-convention.md` | 0 | ✓ |
| 阅读量：L0 必读 ≤ 250 行 | `wc -l` | AGENTS 71 + context-index 109 + task-levels TL;DR 5 = 185 | ✓ |
| 工具层：3 命令 exit 0 | 见上表 | 全 0 | ✓ |

spec `## 验收` 全部条目独立复跑达成。**注意**：验收达标 ≠ 评审通过——B1 是 verify 落点硬门禁违规，独立于 spec 验收。

---

## 🔴 B1（Blocking）：spec `## 验证证据` 段未填

**位置**：`docs/specs/2026-08-09-ai-reading-path-restructure.md` line 277–285

**事实**（本 session 直读 + `rg` 确认）：

```markdown
## 验证证据（实施 session 末尾必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |          ← 空表，仅表头 + 空行

未跑项：               ← 空

> 本段由**实施 session**填写；规划 Session 不允许填写。
```

对照 plan 末尾同名段：8 行已填 + `未跑项：无`。**双份仅 plan 落字，spec 未落字。**

**违规依据**（本 session 原文复核，非采信交接文档转述）：

1. [l2-multi-session-runbook.md](../../template/docs/ai/runbooks/l2-multi-session-runbook.md) "verify 落点（统一）"：*"spec 与 plan 双份各自末尾的 `## 验证证据` 段是 verify 报告的唯一落点……实施 session 必须……写回到 spec 与 plan 两份文件的 `## 验证证据` 段"*
2. 同文"verify 落点细则"：*"两份均必填，**不**接受只填其中一份"*；*"任何'只填一份'视为 verify 报告未完整"*
3. 同文"完成定义"：*"实施 session 跑过 verify 且结果**同时**写入 spec 与 plan 双份……不允许'只填一份'"*
4. [review-checklist.md](../../template/docs/ai/checklists/review-checklist.md) "verify 落点检查"：*"`## 验证证据` 段**同时**出现在 spec 与 plan 双份末尾；**不**接受'只填一份'"*

**自相矛盾点**：实施者自己的 plan `## 验证证据` 段抬头就写 *"两份均必填，不接受'只写 spec 或只写 plan'"*——却只填了 plan 一份。规则被写进了交付物，却未被自身执行。

**ADR-0002 措辞张力（记录，不改变判定）**：[ADR-0002](../../template/docs/adr/0002-verify-hard-gate.md) 原文写"spec **或** plan 文件的 `## 验证证据` 段落"（"或"），而 runbook/checklist 收紧为"双份"。两处措辞不一致。但本 session 评审以 runbook + review-checklist（操作层权威）为准——二者均明文"双份必填"，且实施者已知此规则（写入了自己的 plan）。故 blocking 判定成立。

**风险**：verify 报告不完整时，后续若只回看 spec 末尾会误判"未跑 verify"，违反 ADR-0002"缺 verify 信号时停在未完成"的反向——把缺失包装成完整。

**返工要求**：补填 spec `## 验证证据` 段（内容可与 plan 一致，因 verify 是同一轮），重跑 3 条验证确认仍全 0，再进合并决策。

---

## 🟡 M1：commit subject 超长（6/9 > 72）

**依据**：[commit-convention.md](../../template/docs/ai/commit-convention.md) line 7 *"subject ≤72 字符"*（格式硬规则）；同文 line 69 *"建议 ≤ 72 字符……超过时把细节下沉到 `<body>`"*（细节软提示）；[review-checklist.md](../../template/docs/ai/checklists/review-checklist.md) *"subject 合规：≤ 72 字符"*。

**实跑**（`git log --format=%s main..HEAD | awk '{print length}'`，含 type/scope/冒号/空格）：

| 长度 | commit |
|---|---|
| 88 | `refactor(context-index): de-rule navigation, consolidate admission gate into task-levels` |
| 82 | `docs(plans): record verification evidence and handoff for reading-path restructure` |
| 82 | `docs: fix CONTEXT.md dual-link ambiguity, add snapshot watermark to dogfood drills` |
| 77 | `refactor(governance): demote ADR from required reading to on-demand reference` |
| 74 | `refactor(runbooks): clarify l2-runbook scope boundary, add tl;dr sync rule` |
| 74 | `refactor(agents): replace linear reading list with layering dispatch table` |

3 条合规（≤72）。

**定级 Minor**：line 7 硬规则 + line 69"建议"存在内部张力；按 review-checklist 审查顺序，commit subject 属"风格/可读性"最低层，非行为回归/边界/验证缺失。不阻塞。

**建议**：超长 subject 把细节下沉 `<body>`（本次各 commit 均无 body）。已提交的 commit 不必为长度单独 amend（amend 需用户授权），后续 commit 注意即可。

---

## 🟡 M3：context-index 残留 stale"本节以本节为准"补丁注

**位置**：`template/docs/ai/context-index.md` "深路径"段

**残留原文**：*"（feature-spec 模板里明确写了'仅 L2 任务使用；非 L2 任务可删除本段'——L3 设计 Session 也要填该段，再流转到 plan；**该含义与 template 原文有出入，本节以本节为准**）"*

**问题**：spec `## 背景` 问题 1 把这句"就地打补丁"列为"路径漂移的现场证据"，重构目标即消除三套打架。重构后冲突源（`context-index-summary.md`，即"template 原文"）已在 Task 2 物理删除——**冲突已不存在，"本节以本节为准"的 override 声明失去所指，现为 stale 残留**，正是 spec 要清除的漂移证据本身。

**风险**：低（不影响链接解析与行为），但违背 spec"单一权威、不再有第二份易漂移源"的意图；新读者会困惑"和谁有出入"。

**建议**：删除该括号补丁注，或改写为中性说明（如"L3 设计 Session 也填 `## Session Handoff`，再流转到 plan"），不再宣称"本节以本节为准"。

---

## ⚪ O1：spec 与 plan 同一 commit

**位置**：commit `2a54761 docs(specs,plans): add L2 spec and plan for AI reading path restructure`

**依据**：[review-checklist.md](../../template/docs/ai/checklists/review-checklist.md) *"spec / plan / implementation / review follow-up 不混合"*。

**判定**：Nit / 可接受。spec 与 plan 皆规划 session 交付物、同一 session 产出，合并一个 commit 可读作"规划切片"。严格读 checklist 可视为混合，但二者非跨角色（无 implementation 混入）。**唯一损失**：spec 须先经用户确认再写 plan 的时序在 git history 里不可见（被压缩进一个 commit）；该时序由 plan `## 全局约束` + `## 批准` 段落字补偿。

**建议**：后续 L2 把 spec、plan 分两个 commit，让"spec 提交 → 确认 → plan 提交"序列在 history 显形。本次不必为此 amend。

---

## ⚪ O2：review-checklist"plan 必含回滚" vs 模板无回滚 slot

**事实**：[review-checklist.md](../../template/docs/ai/checklists/review-checklist.md) "spec/plan 双文件检查"列 plan 必含字段含 `回滚`；但 [implementation-plan.md](../../template/docs/ai/templates/implementation-plan.md) 模板**无 `## 回滚` slot**（本 session `rg "回滚|rollback"` 确认）。spec 自身也写"回滚路径属于 plan"——三方期望 plan 有回滚，模板却不提供。

**判定**：非 plan 缺陷。实施者照模板写，模板无 slot 则不填，合理。这是**治理文档自身不一致**（checklist + spec 期望 vs 模板未承载）。

**建议**：二选一统一——要么给 implementation-plan 模板加 `## 回滚` slot（并补示例 `git revert <commit> 逐 Task 回退`），要么从 review-checklist 的 plan 必含字段去掉"回滚"。本次重构未触及模板骨架（spec 非目标明确"不动模板骨架字段"），故不要求本次修；作为 follow-up 记录。

---

## spec/plan 双文件检查（[ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md)）

| 检查项 | 结果 |
|---|---|
| spec 与 plan 物理分离（两独立文件） | ✓ spec 在 `docs/specs/`、plan 在 `docs/plans/` |
| spec 必含字段齐全（背景/目标/行为/非目标/验收/受影响边界/备选方案/风险） | ✓ 8 项全齐 |
| plan 必含字段齐全（文件清单/任务切片/步骤/命令/验证/回滚/`> 基于 spec：` 行） | △ 6/7：缺 `## 回滚`（见 O2，模板无 slot，非缺陷） |
| plan 顶部 `> 基于 spec：` 行 | ✓ 存在，引用 spec 路径 |
| spec 不含 plan-only 字段（任务切片/步骤/文件清单） | ✓ spec 显式声明"不写执行切片"；"需要更新的文档"为 scope 描述非 execution manifest，可接受 |
| plan 不含 spec-only 字段（备选方案/非目标） | ✓ plan 无备选/非目标段（"全局约束"为执行约束非 spec 非目标） |

**spec/plan 物理分离判定：通过。**

## verify 落点检查（[ADR-0002](../../template/docs/adr/0002-verify-hard-gate.md) + runbook）

| 检查项 | 结果 |
|---|---|
| `## 验证证据` 段同时出现在 spec 与 plan 双份末尾 | ✗ spec 段在但空表未填（B1） |
| 实施 session 跑过 verify（命令/退出码/关键输出已落字） | △ 仅 plan 落字；spec 未落字 |
| 规划 session 未填 `## 验证证据` | ✓ spec 段保持空白，header 注"规划 Session 不允许填写" |

**verify 落点判定：未通过（B1）。**

## spec 是否先经用户确认

**判定：通过（基于 artifact 证据）。**

- spec `## Session Handoff`：`Status: blocked（等待用户对 spec 的确认信号）`；`Next Allowed Actions: 用户确认 spec 后 → 写 plan`；`Prohibited Scope: 不得在用户确认前写 plan`
- plan `## 全局约束`：*"spec 已由用户确认（会话消息'确认 spec，继续 plan'）"*
- plan `## 批准`：*"spec 已由用户'确认 spec，继续 plan'信号确认"*

按评审独立性，本 session 不读实施 chat；以 plan 落字的确认信号为证据。spec 的 blocked → plan 的 confirmed，时序一致。✓

> 注：无法从 artifact 独立证实"每条 commit 均经用户实时授权"（那需读 chat，评审纪律禁止）。但 L2 plan 已确认 + 各 commit 匹配 plan 切片 + 无 `--no-verify`/force push/amend 痕迹，提供合理覆盖。AI 硬约束未发现违规信号。

## L3 批准范围检查

不适用（本任务 L2，无 `## 批准` 段硬要求；spec/plan 均正确留空并注明"L2 非必填"）。✓

## 提交边界与 verify 证据

| 检查项 | 结果 |
|---|---|
| 一次提交对应一个可独立验证切片 | ✓ 9 commit = 1 规划（spec+plan）+ 7 Task + 1 verify/handoff 收尾；每 Task 末尾验证 |
| Conventional Commit type 合规（11 白名单） | ✓ 全用 `docs`/`refactor` |
| subject 合规 ≤72 | ✗ 6/9 超长（M1） |
| breaking change 标记 | N/A（无 breaking） |
| AI 行为硬约束（不自动 commit/不跳 hooks/不擅 amend/不 force push/不改 user.name） | ✓ 未发现违规痕迹 |
| PR 描述最小字段 | N/A（未开 PR，评审后由 finishing-a-development-branch 决定） |
| verify 证据回链一致 | ✗ spec 段空（B1） |

## 行为回归 / 边界破坏 / 测试缺口 / 可读性（审查顺序）

1. **行为回归**：无。纯文档结构重构，3 条治理脚本（doctor/link/governance）+ naming 全 0，删 summary 后无断链（link check 覆盖）。治理语义未改（spec 非目标守住：分级条件/验证档位/提交规则/ADR 结论/Adoption Profile 10 字段/模板骨架均未动，本 session 抽样 `rg` 确认）。
2. **边界破坏**：无实质。入口权威从三处收敛为一处（context-index），分流表成为 AGENTS 末尾唯一入口权威——本 session 走查分流表 L0/L1/L2/L3 行可达、自洽。唯一残留边界语义瑕疵见 M3（stale override 注）。
3. **验证缺失**：B1（spec verify 段未填）——见上。
4. **测试缺口**：见下"测试盲区"。
5. **可读性**：M1（commit subject 超长）；其余文档可读性良好，TL;DR 段落 3-5 行符合 spec。

## 测试盲区清单（必填）

| 盲区 | 风险 | 是否需要补 |
|---|---|---|
| 分流表"触发型"列可达性未做 L0 新会话人因模拟 | 中（分流表是入口唯一权威；若某 L 级必读集遗漏，AI 少读） | 是，建议补一次 L0/L1 视角人工走查分流表（spec 验证计划提到此策略，plan 验证证据表未落字其执行） |
| 5 个新 TL;DR 与正文一致性无自动化校验 | 低-中（doc-rewriting-rules 已加"同源同步"提示，靠人维护） | 建议抽样核对 1-2 个 TL;DR 与正文一致性 |
| 删 summary 后历史 plan（2026-08-01-batch-and-dogfood）的 summary 引用 | 低（plan 称为反引号纯路径非链接，link check 0 broken 佐证） | 否，已由 link check 覆盖 |
| 纯文档重构无运行时行为 | 低（spec 声明无需 e2e，doctor+link+governance 为端到端覆盖） | 否 |

剩余风险：除上述外，未发现其他盲区。分流表人因走查是唯一建议补的中风险项。

## 未跑项清单（必填）

对照 plan `## 验证证据` 段"未跑项：无"：

| 验证项 | 实施汇报标注原因 | 评审者判断 |
|---|---|---|
| doctor / link / governance / naming | plan 标"无未跑项" | 接受；本 session 复跑全 0，一致 |
| e2e | spec 声明纯文档无需 e2e | 接受 |
| L0 分流表人因模拟 | plan 未列入验证项（spec 验证计划有此策略但 plan 切片未承载为可执行步骤） | 部分接受——属建议补的人因验证，非 plan 声明的未跑项；不阻塞，但建议补 |

无 plan 显式标注的未跑项需确认；唯一"应跑未跑"= L0 分流模拟，归入测试盲区建议。

---

## 返工要求与后续

**阻塞（须修后才能合并）**：
- B1：补填 `docs/specs/2026-08-09-ai-reading-path-restructure.md` 末尾 `## 验证证据` 段（内容可与 plan 一致，同一轮 verify），重跑 3 条验证确认仍全 0。

**非阻塞 follow-up（可同批或后续）**：
- M1：后续 commit subject ≤72，超长细节下沉 body（已提交不必 amend）。
- M3：删/改写 context-index 深路径段 stale"本节以本节为准"补丁注。
- O2：统一 review-checklist"plan 必含回滚" 与 implementation-plan 模板（加 slot 或删字段）——属治理文档自身一致性，非本任务范围。

**返工后流程**：B1 修完 + 验证复跑全 0 → 进入 [finishing-a-development-branch](#) 决策（合并 main / 开 PR）。若选择开 PR，PR 描述须含目标/范围/非目标/验证证据/风险·回滚，并 `Refs:` 到 spec + plan + 本 review。

---

> 评审 session 完成，交付物：review report at `docs/reviews/2026-08-09-ai-reading-path-restructure-review.md`。
> 判定：返工（B1 阻塞 + M1/M3/O1/O2 非阻塞）。返工后由实施 session 接收（按 [receiving-code-review](#)：技术性核实反馈，不盲从不盲拒）。
