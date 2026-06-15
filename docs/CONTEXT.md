# 仓库术语表（CONTEXT）

> 本文档集中定义仓库内 AI 治理使用的术语。**仅含术语与简短定义，不含规则**——规则在各单点文件 / ADR 中。
>
> 新增 / 修改术语时，必须在 [doc-rewriting-rules.md](ai/doc-rewriting-rules.md) 的"强制回写四类场景"下找到对应触发条件，并把术语登记 / 更新到本文件。
>
> 本文件不替代 AGENTS.md / 单点文件 / ADR；遇到冲突时以单点文件 / ADR 为准。

## 治理结构术语

### 准入门禁（Admission Gate）
"AI 在执行某动作之前**必须**收到的信号"。例如：L2 spec + plan 双份就位、L3 收到用户"已批准"信号、commit 前 review 通过。

### 验证层 vs 准入层
- **验证层**：判断"改动是否成立"（CI 跑 verify、verify 报告落字、测试盲区被列出）。可阶段 0 接入。
- **准入层**：判断"改动是否被允许发生"（L3 Pre-Implementation Approval Gate、L2 spec 准入）。变更"是否开始实施"。

CI 是验证层，不替代准入层。详见 [ADR-0002](adr/0002-verify-hard-gate.md) 与 [ADR-0005](adr/0005-l3-approval-gate.md)。

### 验证基线（Verification Baseline）
按风险等级分层的最小验证要求（L0 / L1 / L2 / L3），单点文件见 [verification-baseline.md](ai/verification-baseline.md)。

### 完成定义（Completion Criteria）
一个任务被视为"完成"必须同时满足的 5 项条件，单点文件见 [completion-criteria.md](ai/completion-criteria.md)。

## 任务结构术语

### 锚点（Anchor）
"最接近行为控制处的文件或符号"。在 task-packet / bugfix-brief / 重构说明中，锚点是修改的主入口；在 spec / plan 中，锚点是受影响的核心文件 / 目录。锚点**不**是"看起来该改的文件"，而是"实际控制目标行为的文件"。

### 行为不变量（Behavior Invariant）
"重构 / 改动后必须保持不变的行为"。在重构工作流中是必填字段；在其他工作流中可选。详见 [refactor-brief.md](ai/templates/refactor-brief.md)。

### verify 报告（Verify Report）
L1+ 任务完成前 AI 必跑的 `verify` 命令的实际结果落字，**必含**：实际命令清单、退出码、关键输出摘要、未跑项及原因。位置：会话汇报 +（L2+）spec / plan 末尾的 `## 验证证据` 段。详见 [ADR-0002](adr/0002-verify-hard-gate.md) 与 [development-runbook.md](ai/runbooks/development-runbook.md)。

### 验证证据（Verify Evidence）
verify 报告中表格化的命令结果，是 verify 报告在 spec / plan 末尾落字时的具体形式。

## 会话 / 角色术语

### 多 session 串行（Multi-Session Serialization）
L2+ 任务**必须**按"设计 / 计划 / 实施 / 评审" 4 个 session 串行推进，会话边界 = 角色边界。详见 [ADR-0003](adr/0003-multi-session-l2.md)。

### 设计 / 计划 / 实施 / 评审 session
- **设计 session**（设计辅助者）：产出 spec
- **计划 session**（计划拆解者）：产出 plan
- **实施 session**（实施者 + 文档维护者）：产出代码 + 测试 + verify 报告
- **评审 session**（审查者，**默认新开**）：产出 review report，含测试盲区清单

### 角色边界 = 会话边界
5 个 AI 角色（设计辅助者 / 计划拆解者 / 实施者 / 审查者 / 文档维护者）**必须**映射到独立 session；不得由单 session 串完全部角色。详见 [ai-role-boundaries.md](ai/ai-role-boundaries.md)。

### 评审独立性
评审 session 必须从零上下文进入，不预读实施 session 的中间对话；只读 `git diff <base>..HEAD`、spec、plan、`## 验证证据` 段。详见 [ADR-0003](adr/0003-multi-session-l2.md) 与 [review-checklist.md](ai/checklists/review-checklist.md)。

## 准入 / 门禁术语

### Pre-Implementation Approval Gate
L3 任务实施 session 启动前必须收用户"明确批准"信号的硬门禁。批准信号必须包含"已批准 / approved / proceed / go-ahead / 确认执行"任一字眼 + 引用具体 spec / plan 路径。详见 [ADR-0005](adr/0005-l3-approval-gate.md)。

### 明确批准 vs 隐含同意
- **明确批准**：包含"已批准"等关键字眼 + spec / plan 路径引用
- **隐含同意**（**不接受**）："看起来不错"、"继续吧"、"嗯"、"👌"等

### 批准范围
批准信号**仅**覆盖 spec / plan 中显式声明的范围；超出范围的改动需要重新批准。详见 [ADR-0005](adr/0005-l3-approval-gate.md)。

### 可撤销批准
用户在实施 session 内任何时刻发出的"撤销批准 / stop / abort"消息立即生效。

## 文档 / 工作流术语

### spec vs plan
- **spec**（feature-spec）：设计准入。必含背景、目标、非目标、受影响边界、备选方案、风险、验证计划
- **plan**（implementation-plan）：执行切片。必含文件清单、任务切片、每切片步骤 / 命令 / 预期结果
- L2 任务**默认**两者都写（详见 [ADR-0004](adr/0004-l2-spec-and-plan.md)）
- plan 抬头必须 `> 基于 spec：[docs/specs/<date>-<name>.md](...)` 一行

### 快速通道
小 L2 任务（< 半天）的例外：合并"设计 + 计划"为 1 session。spec 顶部加 `## 快速通道` 段并简述理由。**此例外不豁免 spec**——快速通道 spec 必须同时含 spec 与 plan 的必含字段。

### L1 → L2 升级
L1 `task-packet` 执行中发现需升级为 L2，必须先把 packet 内容**展开为 spec + plan 双份**进入仓库再继续实施；不允许"边写代码边补 spec"。

### 测试盲区清单
review report **必含**的清单，列出"评审者没看到测试覆盖的场景"。无论是否发现盲区，都必须填写。

### 未跑项确认
review report **必含**的清单，对照实施 session 的 `## 验证证据` 段中"未跑项"逐一确认是否被合理说明。

## 验证 / 测试术语

### verify 命令
项目根目录的 `verify` 入口，串联 lint → typecheck → test → test:e2e → build。各项目**必须**在 manifest 中定义。详见 [verification-baseline.md](ai/verification-baseline.md)。

### CI 是验证层
CI 跑 `verify` 命令的事实记录属验证层；CI 模板可在阶段 0 接入用于加固 verify 必跑纪律。CI **不**替代 L3 Pre-Implementation Approval Gate（这是准入层）。

## 单点定义映射

| 关注点 | 单点文件 | ADR |
|---|---|---|
| 任务分级 | [task-levels.md](ai/task-levels.md) | [0001](adr/0001-task-level-governance.md)（被 0004 修订） |
| 完成定义 | [completion-criteria.md](ai/completion-criteria.md) | — |
| 验证基线 | [verification-baseline.md](ai/verification-baseline.md) | [0002](adr/0002-verify-hard-gate.md) |
| 分支策略 | [branch-strategy.md](ai/branch-strategy.md) | — |
| AI 角色边界 | [ai-role-boundaries.md](ai/ai-role-boundaries.md) | [0003](adr/0003-multi-session-l2.md) |
| 文档回写规则 | [doc-rewriting-rules.md](ai/doc-rewriting-rules.md) | — |
| L2 spec + plan | [task-levels.md](ai/task-levels.md) | [0004](adr/0004-l2-spec-and-plan.md) |
| L3 审批门禁 | [task-levels.md](ai/task-levels.md) | [0005](adr/0005-l3-approval-gate.md) |
