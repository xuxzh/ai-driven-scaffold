# spec / plan 命名与元信息规范

> **这是单点定义文件**。所有 spec (`docs/specs/...`) 与 plan (`docs/plans/...`) 的文件命名、抬头元信息、状态机、主题检索方式按此文件。

## 适用范围

- `docs/specs/<date>-<name>.md`
- `docs/plans/<date>-<name>.md`
- `docs/task-packets/<date>-<name>.md`

> **适用差异**:命名格式(下文)三类资产统一;`## 元信息` 段与状态机**仅 spec / plan 必填**,task-packet 是一次性 L1 资产,不适用元信息段与状态机(详见各自模板)。

设计原则参见 [ADR-0004](../adr/0004-l2-spec-and-plan.md);本文档落地 ADR-0004 中未约束的命名细节与元信息字段。

## 路径基准

- `docs/specs`、`docs/plans`、`docs/task-packets` 路径**相对于项目根**。
- monorepo:改动落在单个子包时,spec / plan / task-packet 放 `<pkg>/docs/specs/`;跨包 L2 放仓库根 `docs/specs/`。
- 命名检查脚本支持子包场景:`python3 scripts/check-spec-and-plan-naming.py --root <pkg>`;doctor 默认查根,子包项目在各包内运行。

## 文件命名

### 粒度

`<date>` 固定为 `YYYY-MM-DD`(日精度,不用月、不带时分)。

理由:

- 月精度无法处理同月内多 L2 任务
- 带时分会破坏文件名字典序的可读性
- `2026-07-01` 长度可控、与 git log 默认时间格式一致

### `<name>` 段

- 小写字母 + 数字 + 短横线(`kebab-case`)
- 长度 2–6 个单词,3 个最常见
- 不使用中文、不使用下划线、不使用大写
- 表达"做什么"而非"为什么做"(理由归 spec 内容)

正例:

```text
2026-07-01-user-auth.md
2026-07-15-fix-import-glob.md
2026-08-03-migrate-pnpm-to-pnpm-v9.md
```

反例:

```text
2026-7-1-UserAuth.md          # 日期精度错 + 大写
2026-07-01-user_auth.md        # 下划线
2026-07-01-为什么做这个.md     # 中文
2026-07-01.md                 # name 缺失
```

### 同日并行

同日启动多个 L2 任务会冲突。冲突处理:

- 第 1 个:`2026-07-01-user-auth.md`
- 第 2 个:`2026-07-01-user-auth-2.md`
- 第 3 个:`2026-07-01-user-auth-3.md`

约束:

- 后缀从 `2` 起,**不补零**(不用 `-02`)
- 后缀紧贴 `<name>`,不带额外分隔
- 不要用 `-a` / `-b` 字母后缀(无法反映启动顺序)

## 元信息段(顶部必填,仅 spec / plan)

每个 spec / plan 文件**必须在正文之前**含 `## 元信息` 段,顺序固定;task-packet 不适用本段:

```markdown
## 元信息

- 主题：auth, jwt, middleware
- 状态：draft
- 关联 ADR：(如 ADR-0004;可省略)
```

字段说明:

| 字段 | 必填 | 取值 | 说明 |
|---|---|---|---|
| 主题 | ✓ | 逗号分隔的小写关键词,2–5 个 | 用于按主题检索历史 spec/plan;不填则无法被主题查询覆盖 |
| 状态 | ✓ | `draft` \| `accepted` \| `superseded` | 见下方状态机 |
| 关联 ADR | ✗ | ADR 文件名(不含路径) | 仅在 spec/plan 显式引用 ADR 时填 |

模板已在 `feature-spec.md` / `implementation-plan.md` 顶部预置 `## 元信息` 段,新写 spec/plan 时**直接复用模板,不要删除该段**。

## 主题检索

```bash
# 列出 auth 主题下所有 spec
rg "^## 元信息" -A 2 docs/specs/ | rg -B 1 "auth"

# 或更直接
rg "^- 主题：.*auth" docs/specs/
```

约定:查询时主题关键词必须出现在 `主题:` 行的逗号列表中,不做 fuzzy 匹配。

## 状态机(仅 spec / plan)

```
   draft ──(实施 session 通过 verify)──> accepted
     │
     └────────(新 spec 覆盖旧 spec)─────> superseded
```

转换规则:

- `draft` → `accepted`:实施 session 跑完 verify 且 spec 的目标全部命中后,由实施者修改
- `draft` → `superseded`:在同主题出现新 spec 且新 spec 显式声明覆盖范围时;**保留**旧 spec,仅改状态
- `accepted` → `superseded`:少见;通常意味着"已完成的设计被新设计整体替换"
- 不允许 `accepted` → `draft`(已接受的设计不能倒退到草稿)

## 不属于本文范围

- spec 与 plan 的**内容分工**(在 [ADR-0004](../adr/0004-l2-spec-and-plan.md))
- 多 session 串行纪律(在 [ADR-0003](../adr/0003-multi-session-l2.md))
- L3 批准门禁(在 [ADR-0005](../adr/0005-l3-approval-gate.md))
- 模板字段在 spec/plan 内容里的具体写法(在 [feature-spec.md](./templates/feature-spec.md) / [implementation-plan.md](./templates/implementation-plan.md))

## 关联

- ADR：[ADR-0004](../adr/0004-l2-spec-and-plan.md)
- 模板：[feature-spec.md](./templates/feature-spec.md)、[implementation-plan.md](./templates/implementation-plan.md)
- 回写规则：[doc-rewriting-rules.md](./doc-rewriting-rules.md)
