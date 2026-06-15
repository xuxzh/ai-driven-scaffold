# ADR-0005 L3 任务 Pre-Implementation Approval Gate（L3 实施 session 启动前必须收用户批准）

日期：2026-06-15
适用等级：L3

## 状态

Proposed

## 背景

`task-levels.md` 对 L3 的规定是仓库内**最严格**的：

> "`L3` 必须人工主导，AI 只作为分析和辅助工具……AI 可以参与生成方案、列出风险、起草 patch 或辅助 review，也可以在明确批准范围内提交受控 patch，但不能在未明确批准的情况下自行推进实现。"

`ai-role-boundaries.md` 的"必须显式审批的场景"段也把 L3 相关改动（CI、部署、依赖、跨 workspace、AGENTS.md 修改等）点名。

但**实际执行上完全没有机制**：

- `branch-strategy.md` 不区分 L3 提交流程
- `verification-baseline.md` L3 验证要求只说"在完整基线外，再人工确认验证范围是否足够"——这是**事后**审查，不是**事前**拦截
- `.claude/settings.json` 没限制 L3 范围的工具
- `.claude/hooks/README.md` hooks 是空的
- 在真实 Claude Code 会话里，AI 完全可能在没有"明确批准"信号的情况下，把 L3 任务一口气做完 patch

也就是说，**L3 在文档里最严，但在执行上最松**。这是治理分级模型里最倒挂的一点。

更具体地：

- L0 已有"分支检查"约束（实质编辑前必须确认不在 main）
- L1 已有"task-packet"约束
- L2 已有"spec + plan"约束（ADR-0004）
- L3 在前 3 级之上**没有任何新增的硬约束**——只多了"AI 不应自行推进"的文档语言

L3 涉及的是仓库内**最不可逆的改动**（依赖升级 / CI 变更 / 部署策略 / 跨 workspace 重构 / 仓库级约定），没有硬门禁意味着**单次事故成本最高**的那一档反而保护最弱。

## 决策

L3 任务在**实施 session 启动前**必须收用户的"明确批准"信号。

### 硬约束范式（可选）

按 ADR-0002 沉淀的"硬约束三件套"句式落地：

> **在 (L3 实施 session 开始) 之前**，AI 必须 **(从仓库文档读到用户的"已批准"信号)**；**汇报 (批准来源与时间)** 于 (实施 session 的会话汇报 + spec/plan 的 `## 批准` 段)；**缺 (明确批准信号) 时 AI 必须停在 (spec / plan 阶段，不得跑 `git add` / `git commit` / patch 等动作)**。

具体的强制规则：

1. **批准信号的形式**：必须包含明确的字眼，如 "已批准" / "approved" / "proceed" / "go-ahead" / "确认执行" 中**任一**；**不**接受"看起来不错 / 继续吧 / 嗯 / 👌"等隐含同意
2. **批准信号必须引用具体 spec/plan 路径**：批准消息中必须出现 `docs/specs/<date>-<name>.md` 或 `docs/plans/<date>-<name>.md` 的完整路径；不引用具体文档的批准视为"未批准"
3. **批准的范围**：仅限 spec/plan 中**显式声明**的范围；实施 session 期间任何"超出 spec/plan 范围"的改动（如新依赖、新文件、新接口）都必须回到批准环节，由用户对**新范围**重新批准
4. **批准的可撤销性**：用户在实施 session 内任何时刻发出的"撤销批准 / stop / abort"消息立即生效；AI 必须停止所有未完成的实施动作并保留未 commit 的改动
5. **预批准机制**：允许在 issue / PR / 仓库 discussion 中预批准某类 L3 改动；spec 顶部必须有 `> 预批准来源：<issue-link>` 段；预批准的范围必须与 spec 声明的范围完全一致
6. **缺信号时 AI 行为**：
   - AI 可以继续读仓库、写 spec、写 plan、跑 verify
   - AI **不**可以跑 `git add` / `git commit` / 直接 patch / 创建 MR / 直接 push
   - AI 必须**显式输出"等待批准"信号**（一段文字"实施 session 等待用户批准：spec at <path>, plan at <path>"），让用户清楚知道现在卡在哪
7. **跨 workspace 改动的特殊要求**：除上述规则外，L3 任务触及跨 workspace / 跨包 / Provider 顺序 / 入口装配顺序时，spec 中必须显式列出**所有受影响的 workspace**；批准信号必须确认"我看了 X、Y、Z workspace 的影响"——一句"已批准"配上一个 workspace 列表的省略，视为未批准

## 后果

- 正向影响：
  - L3 任务的"首次响应"变慢，但**单次事故成本**显著降低
  - 用户的"明确批准"成为可追溯的对话节点（"我说过批准"和"AI 自行推进"被显式区分）
  - 与 ADR-0003 多 session 框架自然衔接：在"设计 → 计划 → 实施"的 3 个 session 切换点之间加一道门控
  - 与 ADR-0004 spec + plan 双写衔接：批准的对象是**双份文档**而非单份，实施 session 启动条件是"双份 + 批准"
  - 与 ADR-0002 verify 必跑衔接：L3 实施 session 仍必跑 verify；批准只解决"是否开始实施"，不解决"实施是否完成"
- 约束或成本：
  - L3 任务的"开始实施"延迟：每条 L3 改动必须等用户显式批准
  - 用户的"批准动作"成本：必须写出明确的"已批准"字眼并引用 spec/plan 路径
  - 实施 session 期间若发现"超出范围"需要回到批准环节；增加中途回退的可能
  - 隐含同意（如"👌"）不被接受；用户必须切换到显式语言
- 后续触发条件：
  - 若 `.claude/hooks/` 引入 `PreToolUse: Bash` 钩子并对 `git add` / `git commit` 增加 L3 spec 路径匹配检查，本 ADR 的"AI 缺信号不得 commit"可由 hook 强制而非依赖 AI 自律
  - 若 PR 模板要求"L3 改动必须引用 spec/plan 路径 + 批准时间"，本 ADR 的"批准必须留痕"可由 PR 描述承接
  - 若 CODEOWNERS 强制 L3 文件必须由指定 reviewer 批准，本 ADR 的"用户批准"可与 CODEOWNERS reviewer 合并为同一信号
  - 若"等待批准"信号被 AI 持续忽略（如 L3 任务 24 小时内未收到批准 AI 仍跑 commit），需要评估是否回退本 ADR 的"软依赖 AI 自律"路径

## 关联

### 前置 ADR

- [ADR-0001](0001-task-level-governance.md)：本 ADR 的 "L3" 作用域来自其分级模型。
- [ADR-0002](0002-verify-hard-gate.md)：本 ADR 继承其"硬约束三件套"句式。
- [ADR-0003](0003-multi-session-l2.md)：本 ADR 在多 session 框架的"设计 → 计划 → 实施"切换点上加一道门控。
- [ADR-0004](0004-l2-spec-and-plan.md)：本 ADR 的批准对象是 spec + plan 双份；批准 + 双份就位 = 实施 session 启动条件。

### 后续 ADR

> 列表为空——本 ADR 是当前 chain 末端。

### 基线文档

- [../ai/task-levels.md](../ai/task-levels.md)（同步修订 L3 段）
- [../ai/ai-role-boundaries.md](../ai/ai-role-boundaries.md)

### 其它

- 模板（待加段）：[../ai/templates/feature-spec.md](../ai/templates/feature-spec.md)、[../ai/templates/implementation-plan.md](../ai/templates/implementation-plan.md)（均加 `## 批准` 段）
