# ADR-0006 AI 阅读路径四层分离与分流入口

日期：2026-08-09
适用等级：全部

## 状态

Accepted

## 修订记录

（初版，留空）

## 背景

本脚手架的 `AGENTS.md` 顶部"治理入口"段曾要求 AI"按以下顺序阅读"11 个文件（含 4 对 summary + full）。诊断发现该阅读路径存在六类问题：

1. **入口路径三套打架**：`AGENTS.md` 治理入口、`context-index-summary` 的"3 分钟短路径"、`context-index.md` 的"短路径"三者第一站与顺序互不一致；`context-index.md` 已就地打补丁（"该含义与 template 原文有出入，本节以本节为准"）。
2. **summary 层 ROI 极低且与 full 严重冗余**：4 个 summary 的标题树几乎是其 full 的子集，全文档图入度仅 2 / 3 / 3 / 3（最低节点），却被摆在"第一入口"位置——占阅读量却无人回引；`commit-convention.md` 还反向指回 summary，形成双向引用。
3. **通读过载**：入口层 11 文件合计约 1403 行，其中 `commit-convention`（提交才读）、`ai-role-boundaries`（L2+ 才读）、`doc-rewriting-rules`（触及长期约定才读）等触发型规则被当成必读。
4. **导航复述规则**：`context-index.md` 一边声明"只聚合入口"，一边塞"准入门禁""验证入口""文档回写规则"复述，制造第二个权威源。
5. **ADR 当操作手册**：`governance-core.md` 要求"ADR 必须与单点文件同步阅读"，把决策依据（why）当操作步骤（how）用。
6. **外围层重复**：`l2-multi-session-runbook.md` 大段复制 `completion-criteria` 五项、`ADR-0002` verify 条款、`ADR-0003` session 序列。

被拒方案及理由：

- **方案 A（保留 summary 改造为纯导航卡片）**：summary 标题 = full 子集，说明无独立信息架构；改造为卡片后仍需与 full 顶部 TL;DR 双向同步，多一个漂移源。删 summary + full 补 TL;DR 更简单。
- **方案 B（保留线性通读，给 11 链加"必读 / 按需"标签）**：只解决问题 3，未解决 1 / 2 / 4 / 5；且把跳过判断推给 AI，不如分流表给确定性必读集。

## 决策

AI 阅读路径采用**四层分离 + 分流入口**，取代线性通读 11 链。

### 四层分离

| 层 | 职责 | 文件 | 读取时机 |
|---|---|---|---|
| 边界层 | 不可破坏的硬边界 + 分流入口 | `AGENTS.md` | 每次必读 |
| 导航层 | 判断顺序 + 跳转链接，零规则 | `context-index.md` | 每次必读 |
| 规则层 | 单点定义，每文件顶部带 TL;DR | `task-levels` / `branch-strategy` / `verification-baseline` / `completion-criteria` / `ai-role-boundaries` / `doc-rewriting-rules` / `commit-convention` | 按级触发 |
| 依据层 | 决策 why，不当操作手册 | ADR-0001~0005 | 有争议才回溯 |
| 模板层 | runbook / template / checklist | 按工作流选 | 走对应流程才读 |

规则层、依据层、模板层全部从必读链降为触发型按需。

### 分流入口

`AGENTS.md` 末尾只保留一张分流决策表：AI 回答"改动是什么级别"（用 `task-levels.md` 判定三问确定 L0/L1/L2/L3）即拿到本次精确必读集，触发型文件发生对应行为时再读。该表是入口唯一权威，其余文件只链接不复述。

### summary 层删除

4 个 `*-summary.md`（context-index / task-levels / branch-strategy / commit-convention）物理删除；其快速浏览价值下沉为对应 full 文件顶部 `## TL;DR` 段（3-5 行）。`commit-convention.md` 删掉反向指向 summary 的链接。

### 导航去规则化

`context-index.md` 移除"准入门禁""验证入口复述""文档回写规则复述"三段；准入门禁清单迁入 `task-levels.md` 各级定义；导航只保留"判断顺序 + 跳转链接 + 代码锚点 + 任务类型分流表"，并成为短/深路径的唯一权威。

### ADR 降为按需回溯

`governance-core.md` 删"ADR 必须与单点文件同步阅读"；改单点文件内"有争议见 ADR-NNNN"式按需引用。硬约束的操作要求已落在单点文件与 runbook（如 verify 必跑写在 `verification-baseline` + `completion-criteria`），ADR 只留"为什么这么定"。

## 后果

- **正向影响**：
  - L0 必读量从 ~1400 行压到 ~250 行（`AGENTS.md` + `context-index` + `task-levels` TL;DR + 锚点）。
  - 导航 / 规则 / 依据 / 模板四层单一权威，不再有第二份易漂移的摘要源。
  - 删 summary 层消除一个双向同步漂移源；`commit-convention` 的双向引用随之消失。
- **约束或成本**：
  - 单点文件顶部 `## TL;DR` 段成为新的维护义务：改正文须同步更新 TL;DR，反之亦然（由 `doc-rewriting-rules.md` "TL;DR 同源同步"提示约束）。
  - 分流表须随 `task-levels` 等级定义变化同步（等级定义变了，必读集跟着变）。
- **后续触发条件**：
  - 新增单点定义文件时，直接落规则层并补 TL;DR，不进必读链。
  - 新增 ADR 时只承载 why，操作面落对应单点文件 / runbook，不当操作手册。
  - 新增触发型规则时，挂到分流表对应等级的"触发型"列，不进必读集。

## 关联

### 前置 ADR

- [ADR-0003](0003-multi-session-l2.md)：多 session 串行；本 ADR 不改其结论，仅调整其被阅读的时机（按需回溯）。
- [ADR-0004](0004-l2-spec-and-plan.md)：spec / plan 分离；本 ADR 不改其结论。

### 基线文档

- [../ai/context-index.md](../ai/context-index.md)：导航层唯一权威，去规则化。
- [../ai/governance-core.md](../ai/governance-core.md)：ADR 定位从"同步阅读"降为"按需回溯"。
- [../../AGENTS.md](../../AGENTS.md)：边界层，末尾分流表为入口唯一权威。
- [../ai/doc-rewriting-rules.md](../ai/doc-rewriting-rules.md)：新增"TL;DR 同源同步"回写规则。
- [../ai/task-levels.md](../ai/task-levels.md)：收口原 context-index 的"准入门禁"清单。
- [../ai/commit-convention.md](../ai/commit-convention.md)：删反向指向 summary 的链接。

### 其它

- 关联 spec：`docs/specs/2026-08-09-ai-reading-path-restructure.md`
- 关联 plan：`docs/plans/2026-08-09-ai-reading-path-restructure.md`
