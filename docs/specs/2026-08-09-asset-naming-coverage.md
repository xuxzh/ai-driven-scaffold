# 资产命名覆盖与路径基准 spec

> 本 spec 仅生成 spec,不替代 plan。L2 任务经用户确认后按 [implementation-plan.md](../../template/docs/ai/templates/implementation-plan.md) 模板产出 plan;spec 与 plan 物理分离(详见 [ADR-0004](../../template/docs/adr/0004-l2-spec-and-plan.md))。

## 元信息

- 主题：naming, task-packet, template, monorepo, doctor
- 状态：draft
- 关联 ADR：ADR-0004

## 背景

现状有三处规范盲区(详见 `docs/specs/2026-08-09-asset-naming-coverage.md` 调研结论):

1. **task-packets 无命名规范覆盖**:`spec-and-plan-naming.md` 的"适用范围"只列 `docs/specs/`、`docs/plans/`;`task-packet.md` 模板顶部无 `## 元信息` 段;`check-spec-and-plan-naming.py` 的 `TARGET_DIRS` 只含前两个目录;`scaffold-doctor.sh` 不检查 `docs/task-packets/` 存在性,也完全不调用命名检查脚本。
2. **template 不带空目录**:`template/docs/` 仅 `adr/`、`ai/`、`CONTEXT.md`;`adoption-checklist.md` 的复制清单只提 `docs/ai/`、`docs/adr/`,新项目接入时 `docs/specs/` 等运行时产出目录无来源。
3. **路径基准未声明**:命名规范写 `docs/specs/...` 是相对路径,未声明基准为项目根;monorepo / 子包场景无说明;`check-spec-and-plan-naming.py` 的 `--root` 已支持子包但未文档化。

为什么现在启动:这三处缺口互相耦合(缺口 1 修了 task-packets 覆盖,但若不接入 doctor 则白加;缺口 2 的目录来源与缺口 1 的检查项强相关),适合一次性收口。

## 目标

把 spec / plan / task-packet 三类交付资产的命名、目录来源、路径基准收口为一致的规范与可验证的检查链路。

## 行为

- `spec-and-plan-naming.md` 的"适用范围"扩展为三类资产(spec / plan / task-packet);命名格式段保持三类统一;元信息段与状态机段标注"仅 spec / plan 必填,task-packet 不适用"。
- `spec-and-plan-naming.md` 新增"路径基准"小节:声明路径相对于项目根;给出 monorepo 规则(单包改动放 `<pkg>/docs/specs/`,跨包 L2 放仓库根);说明 `check-spec-and-plan-naming.py --root` 的子包用法。
- `task-packet.md` 模板顶部加一行指向 `spec-and-plan-naming.md` 的链接;**不**加 `## 元信息` 占位段。
- `check-spec-and-plan-naming.py` 的 `TARGET_DIRS` 增加 `docs/task-packets`。
- `scaffold-doctor.sh` 增加 `docs/task-packets` 存在性检查(与 `docs/specs`、`docs/plans` 对齐);并在 `--template` 与 `--adopted` 两种模式下都调用 `check-spec-and-plan-naming.py`,把命名违例计入 doctor 输出与退出码。
- `template/docs/` 下新增 `specs/.gitkeep`、`plans/.gitkeep`、`task-packets/.gitkeep` 三个空目录占位。
- `adoption-checklist.md` 的复制清单补"`docs/specs`、`docs/plans`、`docs/task-packets`(空目录,承接运行时产出)";人工检查项"`docs/specs/` 和 `docs/plans/` 存在"扩为三项,含 task-packets。
- `template/scripts/tests/test_check_spec_and_plan_naming.py` 补 task-packets 用例(合法 / 非法各一)。

## 非目标

- 不改 `spec-and-plan-naming.md` 的文件名(保留原名,接受文件名与内容轻度不符,换取零链接改动面)。
- 不给 `task-packet.md` 加 `## 元信息` 段或状态机(task-packet 是一次性 L1 资产,套用 draft/accepted/superseded 语义不成立)。
- 不在 Adoption Profile 增加 `Spec Root` / `Plan Root` 配置字段(绝大多数项目用根 `docs/`,加配置是未被请求的灵活性)。
- 不让 doctor 自动 `mkdir` 建目录(doctor"只读文件,不自动修复"边界不变)。
- 不改 `feature-spec.md` / `implementation-plan.md` 模板结构。
- 不处理 `spec-and-plan-naming.md` 命名检查未接入 doctor 以外的其它 doctor 增项。

## 验收(外部可判据)

- `bash template/scripts/scaffold-doctor.sh --template` 退出码 0,0 fail。
- `bash template/scripts/scaffold-doctor.sh --adopted` 在缺 `docs/task-packets/` 目录时对该项 FAIL(新增检查生效)。
- `python3 template/scripts/check-spec-and-plan-naming.py --root .` 对 `docs/task-packets/` 下的非法命名(如 `foo.md`)报违例,对合法命名(如 `2026-08-09-x.md`)不报。
- `scaffold-doctor.sh` 的输出中包含命名检查脚本的调用痕迹(违例文件被列出 / 无违例时该项 PASS)。
- `template/docs/specs/.gitkeep`、`template/docs/plans/.gitkeep`、`template/docs/task-packets/.gitkeep` 三个文件存在。
- `adoption-checklist.md` 含 `task-packets` 检查项与复制清单条目。
- `spec-and-plan-naming.md` 含"路径基准"小节,且"适用范围"段出现 `docs/task-packets`。
- `test_check_spec_and_plan_naming.py` 新增 task-packets 用例,`python3 -m pytest template/scripts/tests/` 全过。

## 范围级别

- 建议任务级别:L2
- 理由:跨多文件行为变化 + 触及长期约定 `spec-and-plan-naming.md` 单点定义 + 改动 doctor 检查链路;不触及 CI / 依赖 / 鉴权,不到 L3。

## 受影响边界

- 命名规范单点定义:`template/docs/ai/spec-and-plan-naming.md`
- 检查链路:`template/scripts/scaffold-doctor.sh`、`template/scripts/check-spec-and-plan-naming.py`、`template/scripts/tests/test_check_spec_and_plan_naming.py`
- 接入指引:`template/docs/ai/checklists/adoption-checklist.md`
- 模板:`template/docs/ai/templates/task-packet.md`
- 模板目录结构:`template/docs/specs/`、`template/docs/plans/`、`template/docs/task-packets/`
- 路由 / 数据流 / 状态边界:无(纯文档与脚本)

## 建议方案

- 命名格式三类统一,元信息 / 状态机只对 spec / plan 强制 → 扩展 `spec-and-plan-naming.md` 适用范围,文件内分节标注适用对象。符合"单点定义"既有模式。
- template 带空目录 + checklist 复制清单补条目 → 新项目整体复制 `template/docs/` 时自动得到空目录;既有项目接入由 doctor FAIL 提示。符合 doctor"只读"边界。
- 路径基准纯文档说明 → 不加配置字段,monorepo 场景靠 `--root` 参数。符合"简单优先"。
- 命名检查接入 doctor → doctor 在两种模式下调用 `check-spec-and-plan-naming.py`,违例计入退出码。补齐"规范定义—脚本检查—doctor 汇总"三层闭环。

## 备选方案

- 方案 A':单建 `task-packet-naming.md`。拒绝:命名规则在两处重复,违背单点定义原则。
- 方案 B':把 `spec-and-plan-naming.md` 改名为 `asset-naming.md`。拒绝:牵动 ADR-0004、context-index、各 runbook、模板等约 5+ 处链接,扩大改动面,违反外科手术原则;文件名不完美可接受。
- 方案 C':在 Adoption Profile 加 `Spec Root` / `Plan Root` 字段。拒绝:绝大多数项目用根 `docs/`,加配置是未被请求的灵活性(YAGNI)。

## 验证计划(仅策略层)

- 最小检查:doctor `--template` 全 PASS + naming check 脚本对三目录合法 / 非法各测一例 + pytest 单元测试全过。
- 边界检查:doctor `--adopted` 在缺 `docs/task-packets/` 时 FAIL;doctor 在既有非法命名(临时构造)时退出码 1。
- 不需要 e2e(纯文档与脚本,无主链路)。

## 风险

- 行为回归风险:doctor 接入 naming check 后,既有仓库的 specs / plans / task-packets 若存在非法命名会让原本 PASS 的 doctor 变红。已预检:本仓库既有文件命名均合法,基线不会变红。
- 边界漂移风险:task-packets 纳入命名检查后,未来 L1 任务包命名必须合规——这是预期收紧,不是回归。
- 落地风险:doctor 调用 naming check 需处理 Python3 可用性;脚本已有 `#!/usr/bin/env python3`,doctor 应以 `python3` 显式调用并容忍缺 python3 时降级为 WARN(避免 doctor 在无 python 环境的项目硬失败)。

## 需要更新的文档

- `template/docs/ai/spec-and-plan-naming.md`(扩适用范围 + 路径基准段)
- `template/docs/ai/templates/task-packet.md`(顶部加链接)
- `template/docs/ai/checklists/adoption-checklist.md`(复制清单 + 检查项)
- `template/scripts/check-spec-and-plan-naming.py`(TARGET_DIRS)
- `template/scripts/scaffold-doctor.sh`(task-packets 存在性 + 调用 naming check)
- `template/scripts/tests/test_check_spec_and_plan_naming.py`(task-packets 用例)
- 新增 `template/docs/specs/.gitkeep`、`template/docs/plans/.gitkeep`、`template/docs/task-packets/.gitkeep`

## Session Handoff

> L2 规划结束,流转到 plan 末尾的 `## Session Handoff` 承接。本 spec 作为状态入口,实施细节见 [docs/plans/2026-08-09-asset-naming-coverage.md](../plans/2026-08-09-asset-naming-coverage.md)。

- Task Level: L2
- Current Phase: spec done, awaiting plan confirmation
- Status: draft
- Next Allowed Actions: 用户确认 spec → 产出 plan → 实施 session 执行 plan
- Prohibited Scope: 不改名 spec-and-plan-naming.md;不加 Adoption Profile 配置字段;不让 doctor 自动建目录

## 验证证据(实施 session 末尾必填)

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| | | | |

未跑项:
