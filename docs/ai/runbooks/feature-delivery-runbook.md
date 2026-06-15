# 业务功能 AI 分会话交付运行手册（4 会话串行版）

## 目的

本文档定义当一个业务功能已经具备接口文档和原型时，如何让 AI 按仓库约定**分 4 个独立 session 串行**完成需求分析、设计、计划、实施和评审。

**默认目标不是让 AI 在一个 session 内生成完整代码**，而是让 AI 在明确边界内受控执行，每 session 留下可回看的交付物与验证证据，下一 session 从仓库文档接力（详见 [ADR-0003](../../adr/0003-multi-session-l2.md)）。

## 适用范围

适用于新增或扩展业务入口、远程数据能力、列表、筛选、表单、详情、操作闭环等需求，且项目内 `verify` 入口已定义。

典型例子：

- 业务资源的新增、编辑、删除、启停
- 有接口文档和原型的业务页面
- 会影响 `数据模型 -> 适配层 -> 查询/缓存层 -> 视图/页面 -> 入口` 多层边界的改动

如果只是文案、局部样式或单个测试修复，可按 `L0` 简化处理，不必完整执行本文档。

## 总体原则

- **会话边界 = 角色边界**：4 个 session 串行，不允许单 session 串完全部 4 个角色
- **设计 session 先收敛需求**，再让后续 session 在边界内执行
- **每 session 结束前**输出"本 session 完成信号"+ 交付物路径，让下一 session 从仓库接力
- **视图/页面不直接写请求逻辑**；入口文件只做装配，不写业务逻辑
- **用户可见行为必须有验证证据**（继承 [ADR-0002](../../adr/0002-verify-hard-gate.md)）
- **AI 汇报时必须说明**：实际运行了哪些命令、哪些通过、哪些未运行及原因

## 任务分级

具备接口文档和原型的业务功能，通常按 `L2` 处理（详见 [task-levels.md](../task-levels.md) 与 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)），因为它往往涉及：

- 跨文件行为变化
- 数据流变化
- 入口或页面状态变化
- 列表、筛选、分页、表单等用户可见交互
- 数据访问、查询、组件、i18n、测试等多处改动

如果需求触及鉴权、权限模型、部署、CI、依赖升级、跨 workspace 重构或仓库级默认约定，应提升为 `L3`，由人工主导并在实施 session 启动前收用户明确批准（详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)）。

## 4 会话串行总览

| Session | 角色 | 必读输入 | 必交付物 | 必跑 verify |
|---|---|---|---|---|
| **设计** | 设计辅助者 | AGENTS.md + context-index + task-levels + 接口/UI 文档 | `docs/specs/<date>-<name>.md` | 不要求 |
| **计划** | 计划拆解者 | 上一 session 的 spec | `docs/plans/<date>-<name>.md` | 不要求 |
| **实施** | 实施者 + 文档维护者 | spec + plan 双份 | 代码 + 测试 + `## 验证证据` 段 | **必须**跑 `verify` |
| **评审** | 审查者（**默认新开 session**） | 实施交付物 + 建议不读实施 session 中间对话 | review report（按 [review-checklist.md](../checklists/review-checklist.md)） | 含"测试盲区"清单 |

L3 任务在"实施 session 启动前"增加一道门：必须先收用户"已批准"信号，详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)。

---

## 第 1 会话：设计（设计辅助者）

**目标**：把接口文档和 UI 原型转化为仓库内可执行的功能设计文档（spec）。

**必读入口**：

- `AGENTS.md`
- `docs/ai/context-index.md`
- `docs/ai/task-levels.md`
- `docs/adr/0004-l2-spec-and-plan.md`（spec / plan 内容分工）
- 项目自身的接口/UI 规范（如有）

**必交付物**：`docs/specs/<date>-<业务功能名>.md`，按 [feature-spec.md](../templates/feature-spec.md) 模板填写。

**必含字段**（spec 必含）：

- 背景、目标、非目标
- 受影响边界（路由 / 数据流 / 状态 / 共享组件 / 工具链）
- 备选方案与拒绝理由
- 风险与未决问题
- 验证计划（**总体策略**，具体命令留给 plan）

**必输出信号**：本 session 末尾输出一段"设计 session 完成，交付物：`docs/specs/<date>-<name>.md`"。

**不允许**：

- 写代码或修改业务文件
- 写 plan（plan 是下一 session 的事）
- 写 verify 报告（验证由实施 session 跑）

**完成后人工检查**：

- 目标是否准确
- 非目标是否足够明确
- 是否存在 AI 自行扩大范围
- 接口字段和 UI 行为是否被正确理解
- 未决问题是否需要先问业务或后端

---

## 第 2 会话：计划（计划拆解者）

**目标**：把 spec 拆成多个可独立验证的实现切片，写入 plan。

**必读入口**：

- 上一 session 产出的 spec
- `docs/ai/templates/implementation-plan.md`（plan 模板）
- `docs/ai/verification-baseline.md`（每切片的 verify 命令应从这里推导）

**必交付物**：`docs/plans/<date>-<业务功能名>.md`，按 [implementation-plan.md](../templates/implementation-plan.md) 模板填写。

**plan 抬头必须**：

```markdown
> 基于 spec：[docs/specs/<date>-<name>.md](...)
```

否则视为与 spec 失联（详见 [ADR-0004](../../adr/0004-l2-spec-and-plan.md)）。

**必含字段**（plan 必含）：

- 文件清单（新建 / 修改 / 测试）
- 任务切片（按可验证切片拆分）
- 每切片：步骤 / 命令 / 预期结果
- 验收标准
- 明确不做什么

**推荐切片顺序**（与多 session 解耦）：

1. 数据模型和字段定义
2. 适配层（service）和接口响应处理
3. 查询/缓存策略和变更失效
4. 列表、筛选、分页、排序
5. 表单、提交、反馈和确认交互
6. 文案（i18n / l10n）
7. 单元测试、页面测试或端到端测试
8. 最终验证和 AI review

**必输出信号**：本 session 末尾输出一段"计划 session 完成，交付物：`docs/plans/<date>-<name>.md`"。

**不允许**：

- 写代码（实施是下一 session 的事）
- 跳过 spec 直接写 plan
- 把 plan 写成 spec 的复制（plan 必须有可执行步骤）

---

## 第 3 会话：实施（实施者 + 文档维护者）

**目标**：按 plan 切片逐步实施，每切片完成即跑对应验证；实施 session 末尾跑 `verify` 并把结果写入 `## 验证证据` 段。

**L3 任务的前置条件**：必须先收用户"已批准"信号（"已批准" / "approved" / "proceed" / "go-ahead" / "确认执行" 任一字眼）并引用 spec/plan 路径。**缺信号时 AI 不得跑 `git add` / `git commit` / 直接 patch / 创建 MR / 直接 push**（详见 [ADR-0005](../../adr/0005-l3-approval-gate.md)）。

**必读入口**：

- 上一 session 产出的 spec + plan 双份
- `docs/ai/branch-strategy.md`（分支 / worktree 选择）
- 项目根目录的 `verify` 命令

**必交付物**：

- 按 plan 切片实施的代码 + 测试
- spec 或 plan 文件末尾的 `## 验证证据` 段（详见下文"必跑 verify"）

**必跑 verify**（继承 [ADR-0002](../../adr/0002-verify-hard-gate.md)）：

- 实施 session 末尾**必须**跑项目根目录的 `verify` 入口
- 把命令的实际退出码与关键输出摘要写入 `## 验证证据` 段
- 未跑项必须显式标注原因
- 缺 verify 报告**不能**声明完成

`## 验证证据` 段格式示例：

```markdown
## 验证证据

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `<pm> lint` | 0 | "All checks passed" | |
| `<pm> typecheck` | 0 | "No errors" | |
| `<pm> test` | 0 | "42 passed" | |
| `<pm> test:e2e` | 0 | "5 passed" | |
| `<pm> build` | 0 | "Build complete" | |
| `<pm> verify` | 0 | "All steps passed" | 完整基线 |

未跑项：`<pm> test:e2e` 在 CI 中跑；本机环境无 headless browser。
```

**L3 任务追加要求**：在 `## 验证证据` 之前增加 `## 批准` 段：

```markdown
## 批准

- 批准时间：YYYY-MM-DD
- 批准来源：<issue-link> / <PR-link> / 会话消息引用
- 批准范围：与 spec 显式声明的范围一致
```

**必输出信号**：本 session 末尾输出"实施 session 完成，交付物：code at <branch> + 验证证据 at <spec-path>#验证证据"。

**注意事项**：

- 视图/页面层不要消费后端原始响应
- 后端字段命名不适合前端时，在 service 或模型层做稳定映射
- 空字符串、undefined、null 的请求语义必须统一
- 分页、筛选、排序不要散落在视图里临时拼接
- 表单 schema 与验证规则独立于视图
- 不要把后端错误结构直接传给 UI

---

## 第 4 会话：评审（审查者，默认新开 session）

**目标**：以独立视角审查实施 session 的交付物，找出行为回归、边界破坏、验证缺失、测试缺口、风格问题。

**必读入口**：

- 上一 session 产出的代码 + spec + plan + `## 验证证据` 段
- `docs/ai/checklists/review-checklist.md`（评审清单）
- `docs/adr/0002-verify-hard-gate.md`（verify 必跑纪律检查）

**建议**：

- **默认新开 session**，从零上下文进入
- **不**预读实施 session 的中间对话；只读 `git diff <base>..HEAD`、spec、plan、`## 验证证据` 段
- 这样可以避免实施 session 的合理化路径污染评审判断

**必交付物**：review report（按 [review-checklist.md](../checklists/review-checklist.md) 结构），**必含**：

- 严重级别 + 文件 + 行为位置 + 风险说明 + 缺失的验证或测试
- "测试盲区"清单（评审者**必填**，未发现也明确写"未发现 + 剩余风险"）
- "未跑项"清单（对照 `## 验证证据` 段的未跑项逐一确认是否被说明）

**必输出信号**：本 session 末尾输出"评审 session 完成，交付物：review report at <path>"。

**评审者不应**：

- 继续扩写功能
- 修改代码（修改代码是实施 session 的事）
- 给出空泛通过结论

---

## 快速通道（小 L2 例外）

若 L2 任务规模 < 半天，可在 spec 顶部加 `## 快速通道` 段并简述合并理由，**合并"设计 + 计划"为 1 session**（仍保留"实施 + 评审"分离）。**此例外不豁免 spec，只豁免 spec 与 plan 的物理分离**——快速通道 spec 必须同时含 spec 与 plan 的必含字段。

## 完成定义

业务功能只有同时满足以下条件，才能称为完成（详见 [completion-criteria.md](../completion-criteria.md)）：

- 4 个 session 的交付物都在仓库内（spec、plan、代码、`## 验证证据`、review report）
- L3 任务有 `## 批准` 段
- 实施 session 跑过 `verify` 且结果已写入 `## 验证证据`
- review report 含"测试盲区"清单
- 触及长期约定时文档已同步更新
- 未执行的验证有明确原因和残余风险说明

## 常见禁区

- 不要一上来让 AI 直接写完整页面
- 不要把请求逻辑直接写进入口或视图组件
- 不要把后端原始响应结构扩散到 UI
- 不要在端到端测试中依赖具体样式类名或脆弱 DOM 结构
- 不要把业务组件默认迁移到共享包
- 不要在没有明确批准时调整入口装配顺序、构建脚本、CI、依赖或仓库级规范
- 不要在没有验证结果时宣称完成
- 不要让实施 session 自己"顺便"做评审——评审必须有独立 session
