# ADR-0002 将 verify 升级为 AI 必跑 + 必汇报的硬门禁

日期：2026-06-15
适用等级：L1 / L2 / L3

## 状态

Proposed

## 背景

仓库最初的 verify 设计是**软建议**：

- `AGENTS.md` 把 `verify` 入口描述为"**建议**在 manifest 中定义 `verify` 串联 lint → typecheck → test → build"
- `verification-baseline.md` 写"各项目**应在**根级 package/manifest 中定义一个 `verify` 命令"
- `completion-criteria.md` 把"必要验证已经执行"列为完成的**硬条件之一**

两处软建议 + 一处硬条件，**三者语气不一致**。在 `.claude/settings.json` 仅限制 `--force` push、`.claude/hooks/README.md` 明确"当前未配置任何 hook"的情况下，AI 在 L1+ 任务完成时**完全可能跳过 verify 后口头宣称完成**——这正是 governance-core.md 写"AI 不是默认决策者，而是受控执行者"想避免的反模式。

更具体地：

- 软建议让 AI 实质上成为自我裁判，与"AI 受控执行"立场相悖
- 完成定义写着"必须"，但执行全靠 AI 自律，文档纪律落不到运行时
- 真实场景中，"应该没问题" 式的口头完成结论比"verify 跑通了 X 命令"更常见

## 决策

verify 升级为**硬门禁**，由三件不可省略的子约束组成：

1. **AI 在 L1+ 任务完成前必须运行项目根目录的 `verify` 入口**。
   - `L0` 任务仍按 `task-levels.md` 的最小验证要求执行；本 ADR 不改变 L0 的轻量特性
   - `L1` / `L2` / `L3` 任务在汇报"完成"之前必须运行 `verify`，否则不能 claim 完成
2. **AI 必须在汇报中给出 verify 的实际结果**。
   - 必含字段：实际运行了哪些命令、命令的实际退出码与关键输出摘要、哪些项未跑及原因
   - 汇报位置：会话内汇报 +（若 L2+ 涉及 spec/plan）spec 或 plan 文件的 `## 验证证据` 段落
3. **缺 verify 信号时，AI 必须停在"未完成"状态**。
   - 即"环境限制无法跑 verify"也必须显式标注；不允许把缺失验证包装成成功
   - 后续动作（merge / 推进下一阶段）由用户决定

仓库内所有"建议"或"应在"的 verify 措辞，**全部替换为"必须"**：

- `AGENTS.md` 顶部"用户项目元信息"中的 `verify` 字段从"建议"改为"必须定义"
- `verification-baseline.md` 的"应在根级 package/manifest 中定义"改为"必须在根级 package/manifest 中定义"
- `completion-criteria.md` 的"必要验证已经执行"段增加"对应 verify 报告"的引用
- `development-runbook.md` 增加"verify 报告"段，说明报告结构与位置

### 硬约束范式（可选）

本 ADR 建立"硬约束三件套"句式：

> **在 (触发条件) 之前**，AI 必须 **(强制动作)**；**汇报 (汇报字段)** 于 (汇报位置)；**缺 (信号) 时 AI 必须停在 (状态)**。

后续 ADR 将复用此句式：

- **ADR-0003（L2+ 多 session）**：在 (开始下一 session) 之前，AI 必须 (读取上一 session 产出)；汇报 (交付物) 于 (spec/plan)；缺 (完成信号) 时 AI 必须停在 (等待状态)
- **ADR-0004（L2 spec+plan）**：在 (进入实施 session) 之前，AI 必须 (收到 spec + plan 双份就位)；汇报 (准入检查结果) 于 (verify 报告)；缺 (任一份) 时 AI 必须停在 (L1 阶段)
- **ADR-0005（L3 Pre-Implementation Approval Gate）**：在 (L3 实施 session 开始) 之前，AI 必须 (收到用户"已批准"信号)；汇报 (批准来源) 于 (会话汇报)；缺 (批准信号) 时 AI 必须停在 (spec/plan)

## 后果

- 正向影响：
  - AI 不能口头 claim 完成；任何"完成"声明都有命令输出可证
  - 与 governance-core 的"AI 是受控执行者"立场一致
  - 把软治理升级为"软治理 + 汇报纪律"，不引入 CI 硬门禁，与 governance-core "不引入过重自动化"的原则兼容
- 约束或成本：
  - AI 的"完成"响应变慢（每个 L1+ 必须跑 verify）
  - verify 跑得慢的项目（例如长时 E2E 套件）会拉高任务完成成本
  - verify 命令必须真实存在；项目若没定义 verify，本 ADR 强制暴露该缺口
- 后续触发条件：
  - 若项目引入 CI 门禁且 CI 跑的 `verify` 与本 ADR 的 `verify` 是同一份命令，本 ADR 的 AI 必跑可降为"AI 必须引用 CI 报告"
  - 若 verify 命令本身设计失败（例如命令经常挂掉或假阳性），需要回到本 ADR 评估是否回退为"AI 必跑 + 必标注失败"
  - 若要进一步硬化为强制门禁，需新增 ADR（不在本 ADR 范围）

## 关联

### 前置 ADR

- [ADR-0001](0001-task-level-governance.md)：本 ADR 的 "L1+" 作用域来自其分级模型。

### 后续 ADR

- [ADR-0003](0003-multi-session-l2.md)：L2+ 任务在多 session 串行上落地为硬门禁。
- [ADR-0004](0004-l2-spec-and-plan.md)：L2 任务默认 spec + plan 双份作为硬门禁。
- [ADR-0005](0005-l3-approval-gate.md)：L3 任务叠加 Pre-Implementation Approval Gate。

### 基线文档

- [../ai/verification-baseline.md](../ai/verification-baseline.md)
- [../ai/completion-criteria.md](../ai/completion-criteria.md)

### 其它

- Runbook：[../ai/runbooks/development-runbook.md](../ai/runbooks/development-runbook.md)
