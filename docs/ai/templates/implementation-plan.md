# 实施计划模板

> **本模板仅用于生成 plan，不替代 spec。** L2 任务的 plan **必须**基于 [feature-spec.md](./feature-spec.md)（或 [bugfix-brief.md](./bugfix-brief.md) / [refactor-brief.md](./refactor-brief.md)）已确认的 spec；spec 与 plan 始终是两份独立文件（详见 [ADR-0003](../../adr/0003-multi-session-l2.md) 与 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)）。
>
> **顶部精确 spec 路径**：下一行 `> 基于 spec：[docs/specs/<date>-<name>.md](...)` **必填**，否则视为与 spec 失联，详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)。
>
> **模板边界**：本模板**不允许**包含设计准入字段——目标、行为、非目标、备选方案、拒绝理由等 spec 必含字段均不属于 plan（详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md) 的"spec 与 plan 最小接口"段）。

> **基于 spec**：[docs/specs/<date>-<name>.md](...)
> （此行**必填**，否则视为与 spec 失联，详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)）

## 元信息

- 主题：(逗号分隔,2–5 个小写关键词,应与基于的 spec 保持一致)
- 状态：`draft` | `accepted` | `superseded`
- 关联 ADR：(可省略)

> 命名规范见 [../spec-and-plan-naming.md](../spec-and-plan-naming.md);文件名前缀为 `<date>-<name>.md`。

> **面向 Agent 执行者：** 步骤使用复选框 `- [ ]` 语法跟踪；如当前会话支持多 agent 调度，可拆给子 agent；否则按手工清单逐任务执行，并保持同样的逐任务验证纪律。

**任务概述（限 2-3 句，本字段仅说「做什么/分几步」，不重复 spec 的目标与行为）：**

---

## 文件清单

- 新建：
- 修改：
- 测试：

### 任务 1：[名称]

**文件：**

- 新建：
- 修改：
- 测试：

- [ ] **步骤 1：编写或更新失败检查**

```text
在这里写出精确的测试、断言或结构化验证内容。
```

- [ ] **步骤 2：运行检查，确认当前状态**

从仓库根目录执行。

执行：

```bash
<pm> test
```

其中 `<pm>` 是项目实际使用的包管理器（pnpm / npm / yarn / uv / cargo / go 等）。

预期：

```text
在这里记录实现前该检查的实际结果。
```

- [ ] **步骤 3：实现最小改动**

```text
在这里写出需要新增或修改的精确代码或文档内容。
```

- [ ] **步骤 4：再次运行验证**

从仓库根目录执行。

执行：

```bash
<pm> test
```

预期：

```text
在这里记录改动后的通过结果。
```

- [ ] **步骤 5：提交**

```bash
git status --short
git add <files>
git commit -m "<message>"
```

这里只是示例。实际执行前，请把暂存文件和提交信息替换成当前切片的真实内容。

---

## 批准（L3 任务必填，其他任务留空）

批准记录的最小必含项详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)；任何字段缺失视为未批准。

- 批准时间：YYYY-MM-DD
- 批准信号：必须包含"已批准" / "approved" / "proceed" / "go-ahead" / "确认执行"任一字眼
- 批准来源：<issue-link> / <PR-link> / 会话消息引用（**未引用视为未批准**）
- 基于 spec 路径：[docs/specs/<date>-<name>.md](...)、本文 plan 路径：[docs/plans/<date>-<name>.md](...)
- 允许修改范围：与 spec `## 目标` / `## 行为` / `## 非目标` 段一致；超出需重新批准
- 禁止范围：明确列出本次不批准的事项（如新依赖、新文件、新接口扩展等）
- 批准跨任务复用：**不允许**；每个新任务必须重新批准

## 验证证据（实施 session 末尾必填）

> **填表要求**：本表必须由**实施 Session** 在跑完项目根目录 `verify` 入口后填写；规划 Session **不允许**填写本表，仅交付 spec + plan 双份（详见 [ADR-0002](../../adr/0002-verify-hard-gate.md) 与 [l2-multi-session-runbook.md](../runbooks/l2-multi-session-runbook.md)）。

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |

未跑项：

> **本段必须落到此位置（`## 批准` 之后）**：spec 与 plan 双份的批准在前、验证证据在后；任何颠倒（如"先验证证据后批准"）视为模板顺序错误。
