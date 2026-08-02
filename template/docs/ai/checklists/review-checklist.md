# AI 评审清单

## 评审 session 独立性（强制）

L2+ 任务的评审 session **默认新开**，且**不**预读实施 session 的中间对话（详见 [ADR-0003](../../adr/0003-multi-session-l2.md)）。

评审 session 仅从以下输入开始：

- 实施 session 产出的代码（`git diff <base>..HEAD`）
- `docs/specs/<date>-<name>.md`
- `docs/plans/<date>-<name>.md`
- 实施 session 末尾的 `## 验证证据` 段（spec 与 plan **双份**均必读；不接受"只填一份"）
- L3 任务的 `## 批准` 段（如有）

**不允许**预读：

- 实施 session 的中间聊天记录
- 实施 session 的"思路说明"（合理化路径）
- 实施 session 的草稿 TODO

这样做的目的：避免评审者被实施者的"我已考虑过"覆盖掉实际的回归、边界破坏、测试缺口。

## L2+ 必查项

以下检查项必须**逐条**对照并写入 review report（"有 / 无 + 位置"）：

### spec / plan 双文件检查（[ADR-0004](../../adr/0004-l2-spec-and-plan.md)）

- [ ] **spec 与 plan 物理分离**：两份独立文件，**不**允许合并为一份
- [ ] **spec 必含字段齐全**：背景 / 目标 / 行为 / 非目标 / 验收 / 受影响边界 / 备选方案 / 风险
- [ ] **plan 必含字段齐全**：文件清单 / 任务切片 / 步骤 / 命令 / 验证 / 回滚 / 顶部 `> 基于 spec：` 行
- [ ] **plan 顶部 `> 基于 spec：` 行存在**：引用 `[docs/specs/<date>-<name>.md](...)`
- [ ] **spec 不得包含 plan 必含字段**（任务切片 / 步骤 / 文件清单）——重复出现视为未分离
- [ ] **plan 不得包含 spec 必含字段**（备选方案 / 非目标）——重复出现视为未分离

### verify 落点检查（[ADR-0002](../../adr/0002-verify-hard-gate.md)、[l2-multi-session-runbook.md](../runbooks/l2-multi-session-runbook.md)）

- [ ] **verify 落点正确**：`## 验证证据` 段**同时**出现在 spec 与 plan 双份末尾；**不**接受"只填一份"
- [ ] **实施 session 跑过 `verify`**：命令清单、退出码、关键输出已落字；未跑项已说明
- [ ] **规划 session 未填 `## 验证证据`**：仅接力交付物；如出现规划 session 写 `## 验证证据`，视为跨 session 责任错位

### L3 批准范围检查（[ADR-0005](../../adr/0005-l3-approval-gate.md)）

- [ ] **`## 批准` 段在 `## 验证证据` 段之前**：模板顺序正确
- [ ] **`## 批准` 段位置**：spec 与 plan 双份均含 `## 批准` 段；不接受"只填一份"
- [ ] **批准记录最小必含齐全**：批准信号（关键字眼）/ spec 路径 / plan 路径 / 允许修改范围 / 禁止范围 / 批准时间——任一项缺失视为未批准
- [ ] **批准范围未扩张**：实施变更严格落在 spec `## 目标` / `## 行为` / `## 非目标` 范围内；任何"超出范围"的改动记为"批准范围扩张，需重新批准"
- [ ] **批准未跨任务复用**：本次批准仅约束当次任务；历史批准不能覆盖本次变更

### 提交边界与 verify 证据（[commit-convention.md](../commit-convention.md)、[ADR-0002](../../adr/0002-verify-hard-gate.md)）

- [ ] **提交边界清晰**：一次提交对应一个可独立验证的切片；spec / plan / implementation / review follow-up 不混合；不得为"提交整齐"塞入无关修改（如 typo 修复、调试代码、未通过 verify 的实验性代码）
- [ ] **Conventional Commit type 合规**：使用 11 类白名单（`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `build` / `ci` / `chore` / `revert`）之一；自定义 type（如 `feat!` 单独写、`bug` / `wip` / `misc`）视为不合规
- [ ] **subject 合规**：≤ 72 字符；祈使语气；不写句号；不堆 emoji / 装饰字符
- [ ] **breaking change 标记一致**：感叹号与 `BREAKING CHANGE:` footer 至少出现一处；若两处皆有，须一致
- [ ] **AI 行为硬约束守住**：未发现 AI 自动 commit（用户未明确要求）、`--no-verify` 跳过 hooks、未授权 `git commit --amend`、`git push --force`、擅自改 `user.name` / `user.email`
- [ ] **PR / MR 描述最小字段齐全**：目标 / 范围 / 非目标 / 验证证据 / 风险·回滚；L2+ 含 `Refs:` 到 spec + plan；引用 issue 时使用 `Closes:` / `Refs:`
- [ ] **verify 证据回链一致**：PR 描述的"验证证据"段与 spec / plan 双份末尾的 `## 验证证据` 段互相引用；评审者按 [commit-convention.md](../commit-convention.md) 的"PR/MR 描述最小字段"段核对

## 审查顺序

1. 行为回归
2. 边界破坏
3. 验证缺失
4. 测试缺口或测试过弱
5. 可读性与可维护性

## 审查前先看哪里

- 仓库级边界先看 `AGENTS.md`
- 治理与完成定义先看 [docs/ai/task-levels.md](../task-levels.md)、[docs/ai/completion-criteria.md](../completion-criteria.md)
- 执行习惯和高频坑先看 [docs/ai/runbooks/development-runbook.md](../runbooks/development-runbook.md)
- verify 必跑纪律先看 [../../adr/0002-verify-hard-gate.md](../../adr/0002-verify-hard-gate.md)

## 核心问题

- 这次改动是否超出了声明目标，影响了额外的用户可见行为？
- 这次改动是否跨过了原本应先写 spec 和 plan 双份的边界？
- 入口装配或数据访问边界是否被隐式改变？
- 涉及主要方法、类、属性的改动，是否补齐了必要注释，并说明了边界或原因？
- 新增或修改的注释是否仍与实现一致，是否存在过期或空泛注释？
- 作者是否运行了当前切片最小但足够的验证？`## 验证证据` 段是否完整？
- 未跑项是否被显式标注并给出原因？是否有残余风险被说明？
- 如果主链路变了，是否考虑了浏览器级或端到端验证？
- 是否有遗漏的文档更新或 runbook 回写？
- L3 任务是否有 `## 批准` 段？批准范围与 spec 显式声明是否一致？

## 问题写法

- 先写严重级别
- 再写文件与行为位置
- 再写风险说明
- 最后写缺失的验证或测试

## 测试盲区清单（必填）

review report 中**必含**"测试盲区"清单，无论是否发现问题：

```markdown
## 测试盲区

| 盲区 | 风险 | 是否需要补 |
|---|---|---|
| 边界值 0/负数/极大 | 低（spec 未要求） | 否 |
| 并发场景 | 中（plan 切片未覆盖） | 是，建议补 |
| i18n 切换 | 低（无国际化要求） | 否 |
| ... | ... | ... |
```

未发现盲区时也要明确写"未发现 + 剩余风险"。

## 未跑项清单（必填）

review report 中**必含**"未跑项"清单，对照 `## 验证证据` 段的未跑项逐一确认是否被合理说明：

```markdown
## 未跑项确认

| 验证项 | 实施汇报中标注的原因 | 评审者判断 |
|---|---|---|
| `<pm> test:e2e` | 本机无 headless browser | 接受；CI 必跑 |
| `<pm> build` | 在 CI 中跑 | 接受；本机不需要 |
| ... | ... | ... |
```

## 无问题时的写法

如果没有发现实质性问题，明确写出"未发现实质性问题"，并补一句剩余风险或测试盲区。**不允许**给出空泛通过结论。
