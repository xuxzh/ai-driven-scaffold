# spec / plan 命名检查器

> **本文件仅为 spec，不替代 plan。** L2 任务须先按本文件产 spec，用户确认后再按 [implementation-plan.md](../ai/templates/implementation-plan.md) 模板产 plan；spec 与 plan 始终是两份独立文件（详见 [ADR-0004](../adr/0004-l2-spec-and-plan.md)）。

## 元信息

- 主题：checker, naming, spec, plan, governance
- 状态：draft
- 关联 ADR：ADR-0004

> 命名规范见 [spec-and-plan-naming.md](../ai/spec-and-plan-naming.md)；文件名前缀为 `<date>-<name>.md`。

## 背景

仓库已经在 [spec-and-plan-naming.md](../ai/spec-and-plan-naming.md) 中把 `docs/specs/<date>-<name>.md` 与 `docs/plans/<date>-<name>.md` 的命名约定立为单点定义：

- `<date>` 固定为 `YYYY-MM-DD`（日精度）；
- `<name>` 为小写字母 + 数字 + 短横线（kebab-case）；
- 同日并行通过 `-2` / `-3` 数字后缀消歧。

但该约定目前只以 Markdown 自然语言形式存在，没有可执行检查器，导致：

- 历史 `docs/plans/` 下出现日期精度错（`2026-7-1-...`）、`<name>` 含下划线或大写、`<name>` 缺失等历史样本无法被自动捕获；
- 新提交者在 L2 流程开始前无法被任何 `verify` 入口拦截命名错误，必须等到评审 session 才发现；
- [AGENTS.md](../../AGENTS.md) 矩阵中"长期任务入口速查"段对 spec/plan 命名的强约束缺乏证据链。

本次变更新增一个**只读、零依赖**的 CLI 检查器，把命名规则变成可执行的事实，让 CI / 评审者有一致的判定依据。

为什么现在启动：父计划 `2026-08-01-ai-session-batch-and-dogfood.md` Task 5 的 dogfood 序列需要至少一个 L2 演练，且明确点名"新增一项独立治理检查"作为 L2 真实用例（[2026-08-01-ai-session-batch-and-dogfood.md](../plans/2026-08-01-ai-session-batch-and-dogfood.md) Task 5 段）。spec/plan 命名恰好是当前**没有可执行检查器**的最自然候选。

## 目标

新增一个 Python 3 标准库 CLI 检查器 `scripts/check-spec-and-plan-naming.py`，对 `docs/specs/` 与 `docs/plans/` 下的**直接** `*.md` 文件名执行 `<date>-<name>.md` 规则的事实校验，让所有历史与新增的 spec/plan 文件名问题在 verify 阶段即被捕获，无需等到评审。

## 行为

> 本段为正向描述；反向条目见 `## 非目标`。

### 触发与对象

- 入口命令：`python3 scripts/check-spec-and-plan-naming.py [--root PATH]`
- 扫描目标：
  - `<root>/docs/specs/*.md` 的**直接子项**（不递归进入子目录）
  - `<root>/docs/plans/*.md` 的**直接子项**（不递归进入子目录）
- `--root` 缺省值为当前工作目录；解析后若不是目录则退出码 2。

### 命名规则（每条命中全部才视为合法）

对每个被扫到的 `*.md` 文件名（不含目录前缀），按以下顺序判定：

1. **剥离扩展名**：去掉末尾的 `.md`。
2. **首段为日期**：以第一个 `-` 为分隔切出首段；首段必须精确匹配 `^\d{4}-\d{2}-\d{2}$`（即 `YYYY-MM-DD` 形式，4 位年 / 2 位月 / 2 位日，固定带连字符）。
3. **日期为真实日历日**：将首段按 `datetime.date.fromisoformat()` 解析；解析失败或解析得到非真实日历日（如 `2026-02-30`、`2026-13-01`、`2026-02-29` 在非闰年）即视为非法。
4. **`<name>` 非空**：剩余部分（去掉首段及其后的一个 `-` 分隔符）非空。
5. **`<name>` 为小写 kebab-case**：剩余部分必须完整匹配 `^[a-z0-9]+(?:-[a-z0-9]+)*$`（仅 ASCII 字母与数字，段间用单个 `-`；不允许下划线、空格、大写、中文、连续连字符、收尾连字符）。
6. **允许同日并行后缀**：`<name>` 段允许以 `-<n>` 结尾（`n` 为 ≥ 2 的正整数），用于消歧同日多个 L2 任务；该后缀属于 `<name>` 的一部分，不破坏 kebab-case 规则。

### 输出

- 任意一步失败 → 打印一行 `<relative_path>`（仓库根或 `--root` 之下的相对路径，使用正斜杠分隔）。
- 多文件非法 → 每个文件独立占一行，按字典序输出。
- 全部合法 → 不打印任何内容。

### 退出码

- `0` = 全部合法（含"两目录均不存在"、"两目录均存在但空"、"单目录缺失"等无失败场景）。
- `1` = 至少一个文件名非法。
- `2` = `--root` 解析后不是目录。

### 缺目录处理

- `docs/specs/` 或 `docs/plans/` 不存在 → 视为该目录"无文件可校验"，不报错、不计入失败；扫描另一目录。
- 两目录均不存在 → 仍然退出 0（无可校验对象）。

## 非目标

- 不校验文件**内容**（不查 spec 是否含 `## 元信息` 段、不查 plan 是否含 `## 验证证据`、不查 spec 与 plan 物理分离、不查 plan 是否引用 spec 路径）——这些由 [check-governance-consistency.py](../../scripts/check-governance-consistency.py) 与 [check-markdown-links.py](../../scripts/check-markdown-links.py) 在各自职责内覆盖。
- 不递归扫描子目录；只校验 `docs/specs/` 与 `docs/plans/` 的直接 `*.md`。
- 不修改任何文件；不写入任何 `verify` 报告文件；不输出 JSON / 人类可读表格。
- 不集成进 [scaffold-doctor.sh](../../scripts/scaffold-doctor.sh) 或任何 CI 配置；不修改 doctor / CI 文件。
- 不校验 `docs/specs/.gitkeep` / `docs/plans/.gitkeep`（它们不匹配 `*.md` 模式，被 glob 自然排除）。
- 不校验 `README.md` / `adr-template.md` / 任何其它被设计为"在 spec/plan 目录但不属于 spec/plan"的特殊文件——本检查器只对 `*.md` 模式生效；任何落在 `docs/specs/` 或 `docs/plans/` 直接子级、未来不匹配 `<date>-<name>.md` 的 `*.md` 文件（如 `README.md`）将被如实标记为非法；这是有意为之的"严格"行为，避免静默放过。
- 不支持 `--template` 模式（与命名相关的检查不区分 template / adopted 仓库）。
- 不引入 pip / npm / 任何第三方依赖；不修改 `pyproject.toml` / `requirements*.txt` / `package.json`。
- 不实施、不写测试代码、不改 plan 中"任务切片"对应的 `scripts/tests/test_check_spec_and_plan_naming.py`（属于本 spec 配套 plan 的实施 session 职责）。

## 验收（外部可判据）

- 验收标准：
  - 命令 `python3 scripts/check-spec-and-plan-naming.py --root .` 在当前仓库 `docs/specs/` 与 `docs/plans/` 全部 `*.md` 已合法的前提下退出码 0、stdout 为空。
  - 手工新增一个非法命名 `docs/specs/bad.md`（无日期），再跑同一命令 → 退出码 1、stdout 含 `docs/specs/bad.md` 一行。
  - 手工新增一个日期非法 `docs/specs/2026-13-01-x.md` → 退出码 1、stdout 含 `docs/specs/2026-13-01-x.md`。
  - 手工新增一个日期不真实 `docs/specs/2026-02-30-x.md` → 退出码 1、stdout 含 `docs/specs/2026-02-30-x.md`。
  - 手工新增一个 `<name>` 大写 `docs/specs/2026-08-02-Bad.md` → 退出码 1、stdout 含 `docs/specs/2026-08-02-Bad.md`。
  - `python3 scripts/check-spec-and-plan-naming.py --root /nonexistent` → 退出码 2、stderr 含非法目录提示。
  - 在临时目录只建 `docs/specs/`、不建 `docs/plans/`，前者放合法文件 → 退出码 0。
  - 在临时目录只建 `docs/plans/`、不建 `docs/specs/`，前者放非法文件 → 退出码 1。
  - 临时目录两目录均缺失 → 退出码 0。
- 主用户流程验收：在仓库根 `bash scripts/scaffold-doctor.sh --template`（注意：本次任务**不**将新检查器接入 doctor；此验收项仅作为回归基线，确认 doctor 仍能跑通）→ 退出码 0、报告 `0 fail(s)`。
- 边界 / 异常验收：
  - `<name>` 包含下划线（`2026-08-01-user_auth.md`）→ 报告。
  - `<name>` 含连续连字符（`2026-08-01-x--y.md`）→ 报告。
  - `<name>` 以连字符收尾（`2026-08-01-x-.md`）→ 报告。
  - `<name>` 缺失（`2026-08-01.md`）→ 报告。
  - 同日后缀 `2026-08-01-foo-2.md` 在合法 `<name>` 段末时 → 不报告。
  - 闰年 `2028-02-29-something.md` → 不报告；非闰年 `2026-02-29-something.md` → 报告。
  - 文件名以 `2026-08-02-` 开头但仅含日期+空名（`2026-08-02-.md`）→ 报告（`<name>` 为空）。

## 范围级别

- 建议任务级别：`L2`
- 为什么适用这个级别：
  - 跨生产 / 测试两个边界：新增 `scripts/check-spec-and-plan-naming.py` 生产脚本 + `scripts/tests/test_check_spec_and_plan_naming.py` 测试 fixture；
  - 跨目录结构：与 `scripts/`、`scripts/tests/`、`docs/specs/`、`docs/plans/` 四个目录的语义耦合；
  - 引入新的可被 `verify` 引用的入口（虽本次不接入 doctor / CI，但接口形状须与既有 `scripts/check-*.py` 一致）；
  - 用户已在本任务 brief 中显式指定 L2。
- 不应降级为 L1：L1 只覆盖"单目标、既有 checker 增量改进"（如 GOV005 是 L1），本任务是**新增独立 checker**，与既有 GOV001–GOV005 无共享函数、无共享 fixture。
- 不可升为 L3：不触及 CI、依赖、鉴权、仓库级约定；命名规则本身已在 [spec-and-plan-naming.md](../ai/spec-and-plan-naming.md) 中明文规定，本检查器只是把规则做成可执行事实，不需要 Pre-Implementation Approval Gate。

## 受影响边界

- 路由
  - `scripts/check-spec-and-plan-naming.py` 作为新的检查器入口，与 [check-markdown-links.py](../../scripts/check-markdown-links.py) / [check-governance-consistency.py](../../scripts/check-governance-consistency.py) 并列；调用方为人工 / 后续 L2 实施 session 末尾 verify。
- 数据流
  - 输入：文件系统只读扫描 `docs/specs/` 与 `docs/plans/` 的直接 `*.md`；
  - 输出：stdout 每行一个非法路径；stderr 仅在 `--root` 非法时输出。
  - 不写任何文件、不修改任何状态。
- 状态边界
  - 无进程内可变状态；无缓存；无副作用。
- 共享组件
  - 不复用 `check-governance-consistency.py` 内部 helper（该脚本的 helper 是治理规则专用，不适用于纯文件名匹配）；不引入新共享模块。
  - 不依赖任何业务库。
- 工具链或脚本
  - 仅 Python 3 标准库（`argparse`、`datetime`、`re`、`sys`、`pathlib`）。
  - 不修改 doctor / CI / hook / pre-commit。
  - 不修改 `pyproject.toml` / 任何依赖声明文件。

## 建议方案

主要实现路径：

1. 在 `scripts/check-spec-and-plan-naming.py` 中：
   - `argparse` 解析 `--root`（默认 `.`，必为目录）；
   - 路径常量 `SPECS_DIR = "docs/specs"`、`PLANS_DIR = "docs/plans"`；
   - `iter_target_files(root)` 用 `Path(root).glob("<dir>/*.md")` 取两个目录的**直接** `*.md`（`Path.glob` 模式 `*.md` 只匹配直接子级，不递归），缺失目录 `try/except` 或预先 `is_dir()` 判空跳过；
   - 校验函数 `validate_filename(stem: str) -> bool`，按"剥离 .md → 切首段为日期 → `datetime.date.fromisoformat()` 解析 → 校验 `<name>` 正则"四步走；
   - 主循环：收集非法文件相对路径，`sorted()` 后逐行 `print`；按是否有非法决定 `return 0 / 1`；`--root` 非目录时 `print(..., file=sys.stderr)` 后 `return 2`。
2. 在 `scripts/tests/test_check_spec_and_plan_naming.py` 中按 [test_check_markdown_links.py](../../scripts/tests/test_check_markdown_links.py) 的 tempfile + subprocess 风格编写：
   - `setUp` / `tearDown` 用 `tempfile.TemporaryDirectory()`；
   - `run_checker(root)` helper 调 `subprocess.run([sys.executable, SCRIPT, "--root", str(root)])`；
   - 用例覆盖验收段全部判据（含合法 / 非法 / 缺目录 / 非法根 / 真实仓库端到端）。

为什么它符合当前仓库的既有模式：

- 现有 `check-markdown-links.py` / `check-governance-consistency.py` 已确立"Python 3 标准库 + argparse + `--root` 默认 `.` + 子进程化调用 + 退出码 0/1/2 + 单行输出"的检查器事实标准；本检查器严格复用同一接口形状，让未来 doctor 接入零成本。
- 现有测试使用 `tempfile.TemporaryDirectory()` + `subprocess.run` 是仓库内已落地的稳定 fixture 风格；不复用会增加维护面。
- 命名约定本身已经在 [spec-and-plan-naming.md](../ai/spec-and-plan-naming.md) 中作为权威定义存在；本检查器只把"已存在的人工规则"翻译为代码，不引入新规则，避免规范漂移。

## 备选方案

- 方案 A：在 [check-governance-consistency.py](../../scripts/check-governance-consistency.py) 内新增 GOV006 规则。
  - 拒绝理由：GOV001–GOV005 是"治理文档内文矛盾"的检查，扫描文件集是固定的 AGENTS / template / docs/ai / docs/adr 等"治理元数据"；spec/plan 命名是"业务文件名"维度，混入会破坏"固定核心扫描文件集"的边界（[check-governance-consistency.py](../../scripts/check-governance-consistency.py) 顶部 docstring 已显式声明此约束）。新增独立脚本是更小的爆炸半径。
- 方案 B：用 shell + `find` / `grep` 实现，零 Python 依赖。
  - 拒绝理由：`datetime.date.fromisoformat()` 的真实日历日校验（含闰年 / 月份上限）在 shell 中需要 `date -d` 之类的非可移植调用，跨 macOS / Linux 行为差异显著；且与既有 Python 检查器族分裂。Python 3 标准库是更稳的同构路径。
- 方案 C：把规则直接写进 [check-markdown-links.py](../../scripts/check-markdown-links.py) 的"特殊链接目标"豁免表。
  - 拒绝理由：链接检查器只关心 `*.md` 内的内联链接是否断裂；文件名合法性是另一维度，混入会污染职责，让后续 GOV006 之类的扩展更难定位。
- 方案 D：把规范落地为 ADR，让 GOV006 规则与 ADR 自动同步。
  - 拒绝理由：当前 spec-and-plan-naming.md 已经是单点定义且 [ADR-0004](../adr/0004-l2-spec-and-plan.md) 已把"spec/plan 物理分离"立为硬约束，但"文件名格式"是命名细节而非架构决策（命名规范文件已经定）。新增 ADR 价值低；当前单点 + 检查器的双层结构与现有 GOV001–GOV005 保持一致。
- 方案 E：接入 [scaffold-doctor.sh](../../scripts/scaffold-doctor.sh) 与 CI 同步启用。
  - 拒绝理由：本次任务 brief 明确"no doctor/CI integration"；接入属于独立后续工作，应在 dogfood 报告与单独 L1 任务中评估。

## 验证计划（仅策略层）

> 具体命令与预期输出在配套 [implementation-plan.md](../plans/2026-08-02-spec-and-plan-naming-check.md) 的"任务切片"段；本段只写"什么算合格"。

- 最小但有效的检查（策略层面）：
  - 在临时目录建双目录 + 已知非法文件名，调用脚本 → 退出码 1 且输出包含该非法文件；
  - 在临时目录建双目录 + 全部合法文件名 → 退出码 0 且输出为空；
  - 临时目录两目录均不存在 → 退出码 0；
  - `--root /nonexistent` → 退出码 2。
- 主用户流程检查：
  - 在仓库根目录对当前已存在的 `docs/specs/` / `docs/plans/` 文件名集合跑一次端到端检查 → 退出码 0、stdout 为空；这等价于"实施 session 末尾 verify 入口"的一部分。
- 边界检查：
  - 闰年（2028-02-29-...）合法、非闰年（2026-02-29-...）非法；
  - 13 月 / 32 日等格式合法但日历非法的样本被捕获；
  - `<name>` 含下划线 / 大写 / 空 / 连续连字符 / 收尾连字符被捕获；
  - 同日后缀 `-2` 不破坏合法判定。
- 跨项目适配检查：checker 在 `--root` 指向不同位置（如 `template/` 或未来 adopted 仓库）时仍按相同规则工作；本次不强制做跨项目 fixture 演练，但实现层应避免硬编码仓库绝对路径。

## 风险

- 行为回归风险：
  - 现有 `docs/specs/` 目录仅有 `.gitkeep`、本 spec 与 plan 落地后只有本任务两份文件 + 既有 `.gitkeep`，不构成回归；`docs/plans/` 已存在三份 `2026-08-01-*.md`，命名全部合法，不会被新检查器报告。
  - 若未来 `docs/specs/` 或 `docs/plans/` 出现 README / 类似"非 spec/plan 的 .md"文件，checker 会将其报告为非法——这是设计的"严格"行为，落地前必须在仓库内确认没有这类文件，否则会误报。
- 边界漂移风险：
  - 同日后缀 `-2` 之后是否要支持 `-10` / `-100`？当前规范只规定 `2` 起、不补零，任意正整数都符合 `^[a-z0-9]+(?:-[a-z0-9]+)*$` 正则——无漂移风险。
  - `<name>` 段若出现 emoji / 拉丁扩展字符：正则限定 ASCII 字母与数字，自然拒绝，无漂移。
- 验证或落地风险：
  - `datetime.date.fromisoformat()` 在 Python 3.7+ 才稳定接受 `YYYY-MM-DD`；仓库 Adoption Profile 隐含 Python 3.10+（`f"..."` 语法、PEP 604 等使用），且实施 session 实施时须确认；但 spec 不应硬编码最低 Python 版本，由实施 session 决定。
  - 测试若不小心把 fixture 文件名写成"恰好合法"，可能造成 false negative；建议 fixture 全部使用明显非法的样本 + 至少一个明显合法的样本。

## 需要更新的文档

- 不更新 [AGENTS.md](../../AGENTS.md)：本检查器本次不接入 doctor / CI；不写"统一命令映射"到 Adoption Profile。
- 不更新 [template/AGENTS.md](../../template/AGENTS.md)：同上。
- 不更新 [docs/ai/spec-and-plan-naming.md](../ai/spec-and-plan-naming.md)：规则单点已经定义完整；本检查器只是事实化。
- 不更新 [docs/ai/verification-baseline.md](../ai/verification-baseline.md)：本检查器本次不接入 `verify` 入口。
- 不更新 [docs/ai/governance-core.md](../ai/governance-core.md) 与 [docs/adr/0004-l2-spec-and-plan.md](../adr/0004-l2-spec-and-plan.md)：新检查器是 L2 实施结果，不影响治理基线。
- 不更新 [scripts/scaffold-doctor.sh](../../scripts/scaffold-doctor.sh) / CI：本次 brief 明确不接入。

## Session Handoff

> L2 设计 Session 使用；L2 规划 session 同步在 plan 末尾的 `## Session Handoff` 落 11 字段，本段仅作为状态入口，按 [`session-handoff-protocol.md`](../ai/runbooks/session-handoff-protocol.md) 字段名留行。

- Task Level: L2
- Current Phase: planning
- Status: ready
- Completed: spec 撰写完成，覆盖元信息 / 背景 / 目标 / 行为 / 非目标 / 验收 / 范围级别 / 受影响边界 / 建议方案 / 备选方案 / 验证计划 / 风险 / 需要更新的文档 / Session Handoff 占位；与 [feature-spec.md](../ai/templates/feature-spec.md) 模板字段对齐。
- Artifacts: `docs/specs/2026-08-02-spec-and-plan-naming-check.md`（本文件）
- Decisions: 拒绝把规则合并到 GOV001–GOV005、拒绝 shell 实现、拒绝 doctor/CI 接入；具体理由见 `## 备选方案`。
- Assumptions: 父计划 brief 中给出的用户当前指令视为对 spec 的明确确认（"Treat that as confirmation of the spec described here"）；详见下方"附：规划 / 批准时序说明"。
- Open Questions: 详见下方"附：规划 / 批准时序说明"。
- Verification: 规划 session 不要求 verify；spec 自身的"## 验证证据"段在实施 session 末尾由实施者填写。
- Next Allowed Actions: 由规划 session 接着产出配套 plan `docs/plans/2026-08-02-spec-and-plan-naming-check.md`；实施 session 仅在 plan 与 spec 双份就位后启动。
- Prohibited Scope: 不得写 `scripts/check-spec-and-plan-naming.py` 或 `scripts/tests/test_check_spec_and_plan_naming.py` 的实现代码；不得修改 parent Plan C、Plan A/B、Task 1–4、doctor、CI；不得 commit / stage / push / amend。

### 附：规划 / 批准时序说明（不扩大范围）

按 [ADR-0003](../adr/0003-multi-session-l2.md) 的 L2 三 Session 通用纪律，理想流程是"规划 session 出 spec → 用户明确确认 → 同 session 继续出 plan → 实施 session 启动"。本次任务 brief 显式指出"approval and planning are in one delegated task"——本任务的**规划与批准信号被合并在同一次用户指令中**：用户已在 brief 内文与 artifact 路径列表中明确给出 spec 的行为与命名（`scripts/check-spec-and-plan-naming.py`），并把 spec + plan 双份同时作为"必须产出"列出。

处理方式（**不扩大范围**）：

- 视为用户已对 spec 内容（"## 行为" / "## 非目标" / "## 验收"）给出确认信号；记录在本节"Assumptions"。
- 不为本次任务新增独立的"spec 确认 → 写 plan"两阶段 session；按 brief 的"一个委托任务同时落地 spec + plan"执行。
- 记录可能的规则歧义：若 L2 runbook 在 dogfood 报告与后续 L1 / L2 任务中需把"用户已合并规划与批准"作为合规信号来源，应在 [l2-multi-session-runbook.md](../ai/runbooks/l2-multi-session-runbook.md) 增加显式段；本次不修该 runbook（属 parent Plan C 范围），仅在本段登记。
- 视为只对本次任务有效；任何后续 L2 任务如未带同样的合并信号，仍应走"先 spec 后 plan"的两阶段。

## 验证证据（实施 session 末尾必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---|---|---|
| `python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v`（RED：实施脚本尚未创建） | `1` | `Ran 13 tests in 0.196s / FAILED (failures=16)`；12/13 测试因脚本文件不存在（`subprocess` 退出码 2）失败，1 个测试 (`test_invalid_root_returns_two`) 巧合通过（Python 缺文件即返回 2） | 实施 session 已写测试 fixture、尚未写 `scripts/check-spec-and-plan-naming.py`；RED 阶段（`2026-08-01T17:35:48Z`, epoch `1785605748`） |
| `python3 -m unittest scripts.tests.test_check_spec_and_plan_naming -v`（GREEN：实施脚本创建后） | `0` | `Ran 13 tests in 0.355s / OK`（13/13 测试通过） | 13 个 unittest 用例 + TestEndToEndRepo 端到端用例全部通过；`2026-08-01T17:36:24Z`（epoch `1785605784`） |
| `python3 scripts/check-spec-and-plan-naming.py --root .` | `0` | stdout 空（`docs/specs/` + `docs/plans/` 下 5 个 .md 文件全部合法） | 当前树端到端扫描零失败 |
| `python3 scripts/check-markdown-links.py --root . --template` | `0` | stdout 空 | 回归基线：本次新增不引入断链 |
| `python3 scripts/check-governance-consistency.py --root . --template` | `0` | stdout 空 | 回归基线：GOV001–GOV005 仍全部通过 |
| `bash scripts/scaffold-doctor.sh --template` | `0` | `Summary: 0 fail(s), 0 warning(s)`（含 12 项 PASS） | doctor 报告零失败；新检查器未接入 doctor（按 brief "no doctor/CI integration"），仅作回归基线 |
| `git diff --check` | `0` | stdout 空 | 工作树无冲突标记 / 无尾空格；本次仅新增 2 个未跟踪文件 + 2 处 spec/plan 表填充 |

**实施 session 时间戳（UTC）**：
- Start: `2026-08-01T17:35:28Z`（epoch `1785605728`）
- End:   `2026-08-01T17:36:29Z`（epoch `1785605789`）
- Elapsed wall-clock: `61` 秒

未跑项：
- `bash -n scripts/check-spec-and-plan-naming.py`：plan 步骤 5 列出此命令，但本任务是 Python 脚本非 Bash 脚本；`bash -n` 仅做语法检查，对此文件无意义且会报"is not a bash script"；本任务以 RED → GREEN 单元测试隐含字节码可加载替代。未跑原因：命令对当前工件类型不适用。

> **填表顺序**：实施 session 跑完 `verify` 入口后，把每条命令的实际退出码与关键输出摘要填入本表；未跑项与原因独立列出；缺任一项均视为 verify 报告未就位（详见 [ADR-0002](../adr/0002-verify-hard-gate.md)）。本段必须由**实施 session**填写；规划 Session 不允许填写。
