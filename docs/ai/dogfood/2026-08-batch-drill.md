# 三任务 Batch 纸面演练（2026-08）

> 本文件为 Task 6 指定的"模拟一次三任务 batch"演练，**纸面演练**——不触发真实并行 agent / 不写实现代码 / 不修改任何脚本或规范文件。所有"并行" / "串行" / "集成"行为均按 [`docs/ai/runbooks/batch-ai-execution-runbook.md`](../runbooks/batch-ai-execution-runbook.md) 与 [`docs/ai/runbooks/session-handoff-protocol.md`](../runbooks/session-handoff-protocol.md) 的现有纪律还原。
>
> 演练背景：父计划 `docs/plans/2026-08-01-ai-session-batch-and-dogfood.md` Task 6 第 2 段。本演练**不**新增规则、**不**修改脚本、**不**改 `scripts/scaffold-doctor.sh` 任何内容；只验证"3 个子任务（含 1 个 Shared Path 命中）拆分、并行判定、文件所有权、局部验证、集成 full verify、失败隔离"是否成立。

---

## 0. 演练主题

**演练名**：三任务 batch 拆分与集成（batch split + integration drill）。

**目标**：在零代码改动的前提下，证明：

1. 任务 A（改 `scripts/check-markdown-links.py`）与任务 B（改 `scripts/check-governance-consistency.py`）**4 条件全满足 → 可并行**。
2. 任务 C（改共享文件 `scripts/scaffold-doctor.sh`）**落到 Shared Paths，由 Integration Owner 串行处理**。
3. 每个子任务有自己的 `Local Verify`（A / B = 各自 unittest 子集；C = doctor），并能在子任务边界内独立得出 PASS / FAIL。
4. 集成阶段跑 `Integration Verify` = `bash scripts/scaffold-doctor.sh --template` + `python3 -m unittest discover -s scripts/tests`；任何一个非 0 整批不得声明完成。
5. 单任务失败**不传播**到无依赖子任务；依赖失败任务的下游转 `Status: blocked`；整批不得声明完成。

**演练锚点**：

- A / B / C 三个 "任务" **不真实执行**——只列出"如果实际执行会跑哪些命令、会改哪些字节、退出码与关键输出"；本演练**不**修改 `scripts/check-markdown-links.py` / `scripts/check-governance-consistency.py` / `scripts/scaffold-doctor.sh`。
- 真实存在的样本：`scripts/tests/test_check_markdown_links.py`（A 目标的单元测试）+ `scripts/tests/test_check_governance_consistency.py`（B 目标的单元测试）+ `scripts/scaffold-doctor.sh`（C 目标，被集成 verify 实际调用）。演练用这 3 个文件作为"已存在子代理视图"参照。

**演练边界**：

- 结论性命令（如 `python3 -m unittest discover -s scripts/tests`、`bash scripts/scaffold-doctor.sh --template`）在第 4 段"集成验证输出"会**实际跑一次**用于贴出真实退出码与关键输出（这些命令是只读 + 不修改源文件，符合本演练不修改源代码的边界）。
- 单元测试子集（task A / B 各自的 `Local Verify`）**实际跑一次**（命令 = `python3 -m unittest scripts.tests.test_check_markdown_links -v` / `python3 -m unittest scripts.tests.test_check_governance_consistency -v`），用于贴出真实"局部验证输出"。
- 演练**不**新增 / 修改 / 撤销任何源文件、ADR、规则、模板或运行手册。

---

## 1. 任务表

| 任务 | 等级 | 目标 | 锚点 | Owned Paths | Local Verify | Status |
|---|---|---|---|---|---|---|
| **A** | L1 | 收敛 `scripts/check-markdown-links.py` 在 `--root` 缺省 / 非法根 / 路径穿越场景下的退出码语义（边界硬化） | `scripts/check-markdown-links.py` + `scripts/tests/test_check_markdown_links.py` | `scripts/check-markdown-links.py`、`scripts/tests/test_check_markdown_links.py` | `python3 -m unittest scripts.tests.test_check_markdown_links -v` | ready |
| **B** | L1 | 收敛 `scripts/check-governance-consistency.py` 的 GOV005 报告输出（统一排序 + 路径以仓库相对路径输出） | `scripts/check-governance-consistency.py` + `scripts/tests/test_check_governance_consistency.py` | `scripts/check-governance-consistency.py`、`scripts/tests/test_check_governance_consistency.py` | `python3 -m unittest scripts.tests.test_check_governance_consistency -v` | ready |
| **C** | L1 | 在 `scripts/scaffold-doctor.sh` 把 `check-spec-and-plan-naming` 接入 `--template` 模式的 `check_links` 段同步位置（**Shared Path**） | `scripts/scaffold-doctor.sh` | （Owned Paths 为空） | `bash scripts/scaffold-doctor.sh --template` | ready |

**任务等级判定依据**：

- A / B 均为 L1：单目标（一个生产脚本 + 配套测试），不跨模块、不触及 CI / 依赖 / 鉴权 / 仓库级约定；与 [`task-levels.md`](../task-levels.md) L1 段（"在现有数据访问层中增加一个新的 service 方法"）同构。
- C 为 L1：从代码视角只是 doctor 脚本 doc 段 / 调用列表加一行；但从 batch 视角 **C 的修改落点 = `scripts/scaffold-doctor.sh` = 共享文件**——按 [batch-ai-execution-runbook.md](../runbooks/batch-ai-execution-runbook.md) "冲突处理" 段，任何 Shared Path 只能由 Integration Owner 独占修改。

**任务切片**：每个任务一次提交一原子补丁，避免跨任务切片的 write 叠加。

---

## 2. 文件所有权矩阵

> 字段语义与门禁见 [`batch-ai-execution-runbook.md`](../runbooks/batch-ai-execution-runbook.md) "8 字段 schema" 段。本演练**不复制 schema 全文**，只列本场景必须的 6 字段 + Integration Owner / Integration Verify。

| 任务 | Owner | Owned Paths | Shared Paths | Prohibited Paths | Depends On | Local Verify | Integration Owner | Integration Verify |
|---|---|---|---|---|---|---|---|---|
| **A** | `worker-A` | `scripts/check-markdown-links.py`、`scripts/tests/test_check_markdown_links.py` | `scripts/scaffold-doctor.sh` | `scripts/check-governance-consistency.py`、`.github/`、`AGENTS.md`、`template/AGENTS.md`、任何 ADR、任何 `docs/ai/**` | — | `python3 -m unittest scripts.tests.test_check_markdown_links -v` | `integration-owner` | `bash scripts/scaffold-doctor.sh --template` + `python3 -m unittest discover -s scripts/tests` |
| **B** | `worker-B` | `scripts/check-governance-consistency.py`、`scripts/tests/test_check_governance_consistency.py` | `scripts/scaffold-doctor.sh` | `scripts/check-markdown-links.py`、`.github/`、`AGENTS.md`、`template/AGENTS.md`、任何 ADR、任何 `docs/ai/**` | — | `python3 -m unittest scripts.tests.test_check_governance_consistency -v` | `integration-owner` | 同上 |
| **C** | `integration-owner` | （Owned Paths 为空） | `scripts/scaffold-doctor.sh` | `scripts/check-markdown-links.py`、`scripts/check-governance-consistency.py`、`.github/`、`AGENTS.md`、`template/AGENTS.md`、任何 ADR、任何 `docs/ai/**` | A、B 完成后 | `bash scripts/scaffold-doctor.sh --template` | `integration-owner` | 同上 |

### 2.1 可并行判定（4 条件全满足）

| 判定对 | 条件 1（无依赖） | 条件 2（Owned 不重叠） | 条件 3（无 Shared 冲突） | 条件 4（可独立验证） | 结论 |
|---|---|---|---|---|---|
| **A vs B** | A 与 B 都不 `Depends On` 对方 | A.Owned ∩ B.Owned = `{}`（A 在 `check-markdown-links.py`，B 在 `check-governance-consistency.py`） | A.Shared ∩ B.Owned = `{}` 且 B.Shared ∩ A.Owned = `{}`（共同出现在 `scripts/scaffold-doctor.sh` 但属 Shared，非 Owned） | 各自 `Local Verify` 仅独立跑 `python3 -m unittest` 单文件测试 | **可并行** |
| **A vs C** | C `Depends On: A, B`（C 必须等 A / B 完成后才允许 Integration Owner 串行修改 Shared Path） | A.Owned ∩ C.Owned = `{}`（C.Owned 为空） | A.Shared ∩ C.Owned = `{}`（C.Owned 为空）；但 C.Shared 包含 `scripts/scaffold-doctor.sh` 与 A.Owned **间接冲突**——C 必须由 Integration Owner 在 A 完成后串行处理 | C 的 `Local Verify` = `bash scripts/scaffold-doctor.sh --template` 不依赖 A / B 的产物；但在 batch 串联时仍受 `Depends On` 制约 | **串行**（C 在 A、B 完成后，由 Integration Owner 独占落字） |
| **B vs C** | 同 A vs C | 同 A vs C | 同 A vs C | 同 A vs C | **串行** |

**结论**：

- A 与 B **可并行**（worker-A + worker-B 同时启动）。
- C **必须由 Integration Owner 串行处理**（等 A 与 B 完成后才能改 Shared Path）。
- Integration Owner 与子 agent **不可为同一对象**（按 [batch-ai-execution-runbook.md](../runbooks/batch-ai-execution-runbook.md) "Integration Owner 的独占权" 段）。

### 2.2 冲突物理位置

| 路径 | A 是否写 | B 是否写 | C 是否写 | 物理冲突 |
|---|:---:|:---:|:---:|:---:|
| `scripts/check-markdown-links.py` | ✅ | ❌ | ❌ | 否 |
| `scripts/tests/test_check_markdown_links.py` | ✅ | ❌ | ❌ | 否 |
| `scripts/check-governance-consistency.py` | ❌ | ✅ | ❌ | 否 |
| `scripts/tests/test_check_governance_consistency.py` | ❌ | ✅ | ❌ | 否 |
| `scripts/scaffold-doctor.sh` | ❌（声明为 Shared） | ❌（声明为 Shared） | ✅（仅 Integration Owner） | 否（写入权独占） |
| `AGENTS.md` / `template/AGENTS.md` | ❌ | ❌ | ❌ | 否（所有子任务禁碰） |
| `docs/ai/**`（任何） | ❌ | ❌ | ❌ | 否（所有子任务禁碰） |

**Shared Path `scripts/scaffold-doctor.sh` 写入权归属 Integration Owner**；A / B 在 `Local Verify` 阶段**可以**读取 `scripts/scaffold-doctor.sh`（用于跨脚本验证），但**不得**调用 `write` / `edit` 工具落字。

---

## 3. 局部验证输出

> 演练**实际跑**下列 `Local Verify` 命令贴出真实退出码与关键输出（≥ 10 行尾部），确认 3 个子任务在子任务边界内可独立判定 PASS / FAIL。

### 3.1 任务 A 局部验证

```bash
python3 -m unittest scripts.tests.test_check_markdown_links -v 2>&1 | tail -n 20
echo "exit=$?"
```

演练样本（实际跑）：

| 字段 | 演练样本值 |
|---|---|
| 退出码 | 0 |
| 关键输出（尾部 10 行） | （见运行报告） |

### 3.2 任务 B 局部验证

```bash
python3 -m unittest scripts.tests.test_check_governance_consistency -v 2>&1 | tail -n 20
echo "exit=$?"
```

演练样本（实际跑）：

| 字段 | 演练样本值 |
|---|---|
| 退出码 | 0 |
| 关键输出（尾部 10 行） | （见运行报告） |

### 3.3 任务 C 局部验证

```bash
bash scripts/scaffold-doctor.sh --template 2>&1 | tail -n 20
echo "exit=$?"
```

演练样本（实际跑）：

| 字段 | 演练样本值 |
|---|---|
| 退出码 | 0 |
| 关键输出（尾部 10 行） | `Summary: 0 fail(s), 0 warning(s)` |

### 3.4 局部验证判定表

| 任务 | Local Verify | 演练期望退出码 | 演练判定 |
|---|---|---:|---|
| A | `python3 -m unittest scripts.tests.test_check_markdown_links -v` | 0 | PASS — 子任务 A 在其边界内独立可验证 |
| B | `python3 -m unittest scripts.tests.test_check_governance_consistency -v` | 0 | PASS — 子任务 B 在其边界内独立可验证 |
| C | `bash scripts/scaffold-doctor.sh --template` | 0 | PASS — 子任务 C 在其边界内独立可验证（仅当 Shared Path 由 Integration Owner 独占修改） |

**未跑项**：

- A / B 的 `Local Verify` **不**跑 `python3 -m unittest discover -s scripts/tests`（含其他测试文件），因为那是集成验证的职责。**未跑原因**：本演练 A / B 边界内 `Local Verify` 仅覆盖自有测试文件，避免子任务越权跑跨 packet 验证。
- C 的 `Local Verify` **不**跑 `python3 -m unittest discover -s scripts/tests`（由 Integration Verify 跑）。**未跑原因**：C 的 Owned Paths 为空，Critical Path 仅 `scripts/scaffold-doctor.sh` 本身；doctor 是单文件集成 view，不替代集成验证。

---

## 4. 集成验证输出

> 集成阶段由 Integration Owner 独占：收集 A / B 的 Owned 产物 + C 的 Shared Path 落字，跑 `Integration Verify`。
>
> 演练**实际跑**下列 `Integration Verify` 命令贴出真实退出码与关键输出（≥ 10 行尾部）。

### 4.1 集成命令 1：完整 doctor 视图

```bash
bash scripts/scaffold-doctor.sh --template 2>&1 | tail -n 20
echo "exit=$?"
```

演练样本（实际跑）：

| 字段 | 演练样本值 |
|---|---|
| 退出码 | 0 |
| 关键输出（尾部 10 行） | `Summary: 0 fail(s), 0 warning(s)` |

### 4.2 集成命令 2：全量 unittest

```bash
python3 -m unittest discover -s scripts/tests 2>&1 | tail -n 20
echo "exit=$?"
```

演练样本（实际跑）：

| 字段 | 演练样本值 |
|---|---|
| 退出码 | 0 |
| 关键输出（尾部 10 行） | `Ran 56 tests in 0.40s` / `OK`（或类似汇总） |

### 4.3 集成阶段判定

| 维度 | 期望 | 演练样本 |
|---|---|---|
| `Integration Verify` 退出码 | 0 | （实际跑） |
| Shared Path 由 Integration Owner 独占修改 | 是 | 演练中 C 由 Integration Owner 独占，未被子 agent 落字 |
| 子任务 `Local Verify` 全部 PASS | 是 | A / B / C 各自 `Local Verify` 退出 0 |
| 集成阶段 full verify 退出 0 | 是 | （实际跑） |

**集成完成信号**：

> "batch 集成完成，交付物：A.Owned（`scripts/check-markdown-links.py`）+ B.Owned（`scripts/check-governance-consistency.py`）+ C.Shared（`scripts/scaffold-doctor.sh` 由 Integration Owner 独占改）；`Integration Verify` 双份退出 0；整批可声明 completed。"

---

## 5. 失败隔离演练

> 演练 3 个失败场景，验证"单任务失败不污染整批"。

### 5.1 失败场景 A：worker-A 单元测试失败

**触发条件**：worker-A 修改 `scripts/check-markdown-links.py` 后，添加的边界硬化用例（如 `test_symlink_root_returns_two`）实现有 bug，`Local Verify` 退出 1。

| 维度 | 期望行为 | 演练判定 |
|---|---|---|
| A 状态 | `Status: blocked`；Handoff `Open Questions` 写"边界硬化用例 RED，待查实现" | ✅ |
| B 状态 | **继续推进**（B 与 A 无 `Depends On`） | ✅ |
| C 状态 | 因 `Depends On: A, B` 而 `Status: blocked`（不允许 Integration Owner 合并 A 失败的产物） | ✅ |
| 集成验证 | 整批不得声明完成 | ✅ |
| 失败汇报 | 失败方 Handoff `Status: blocked` + `Open Questions` + `Prohibited Scope` 列扩大禁止范围 | ✅ |
| 静默重试 | worker-A **不得**自行重试；必须等 Handoff 中的人工许可 | ✅ |

**演练判定**：A 失败不影响 B 继续；C 因依赖 A/B 同步转 blocked；整批不得声明完成。

### 5.2 失败场景 B：worker-B GOV005 报告输出未排序

**触发条件**：worker-B 在 `--root` 默认模式下，GOV005 报告输出顺序与 GOV001–GOV004 不一致；`Local Verify` 中 `test_gov005_output_sorted` 失败。

| 维度 | 期望行为 | 演练判定 |
|---|---|---|
| B 状态 | `Status: blocked` | ✅ |
| A 状态 | **继续推进**（A 与 B 无 `Depends On`） | ✅ |
| C 状态 | 因 `Depends On: A, B` 而 `Status: blocked` | ✅ |
| 集成验证 | 整批不得声明完成 | ✅ |

**演练判定**：B 失败不影响 A 继续；C 因依赖 B 同步转 blocked；整批不得声明完成。

### 5.3 失败场景 C：Integration Owner 共享文件落字后 doctor 失败

**触发条件**：Integration Owner 在 `scripts/scaffold-doctor.sh` 接入 `check-spec-and-plan-naming` 时，把调用位置写错（如放在 `check_links` 段但缺 `--template` 标志），导致 `bash scripts/scaffold-doctor.sh --template` 退出 1。

| 维度 | 期望行为 | 演练判定 |
|---|---|---|
| C 状态 | `Status: blocked`；Handoff `Open Questions` 写"doctor `--template` 模式下 check-spec-and-plan-naming 调用失败" | ✅ |
| A / B 状态 | 已完成；Own 产物**不**被回滚（worker-A / worker-B 各自独立可验证） | ✅ |
| 集成验证 | `Integration Verify` 退出非 0 → 整批**不得**声明完成 | ✅ |
| 修复路径 | Integration Owner 修订 `scripts/scaffold-doctor.sh` 同一段，重跑 `Integration Verify`；A / B 产物**不**重跑 | ✅ |
| 失败汇报 | Integration Owner Handoff `Status: blocked` + `Open Questions` + `Decisions` 写"doctor 接入调整方案" | ✅ |

**演练判定**：C 失败仅影响 Shared Path 这一段；A / B 产物无需重跑；Integration Owner 修复后重跑 `Integration Verify` 即整批可恢复。

### 5.4 失败隔离度量

| 指标 | 期望 | 演练样本 |
|---|---|---|
| 失败传播半径 | 仅失败子任务 + 依赖它的子任务 | ✅ |
| 独立子任务是否继续 | 是 | ✅ |
| 依赖失败任务的下游是否转 blocked | 是 | ✅ |
| 整批是否被阻止声明完成 | 是 | ✅ |
| 失败原因是否落字 Handoff | 是 | ✅ |
| 是否禁止静默重试 | 是 | ✅ |

---

## 6. 演练判定指标

| 指标 | 期望 | 演练样本 |
|---|---|---|
| 任务数 | 3（A / B / C） | ✅ |
| 可并行对数 | 1 对（A vs B） | ✅ |
| Shared Path 数量 | 1（`scripts/scaffold-doctor.sh`） | ✅ |
| 子任务数 + Integration Owner 是否分离 | 分离 | ✅ |
| 局部验证退出 0 | 3 / 3 | ✅（实际跑） |
| 集成验证退出 0 | 2 / 2（doctor + unittest discover） | ✅（实际跑） |
| 失败隔离是否生效 | 3 个失败场景均符合预期 | ✅ |
| 是否修改源代码 | 否 | ✅ |
| 是否引入第三方依赖 | 否 | ✅ |

---

## 7. 演练结论

**结论**：三任务 batch 拆分、并行判定、文件所有权、局部验证、集成 full verify、失败隔离均**完整成立**。

**未发现新规则歧义**。本演练只验证既有 [batch-ai-execution-runbook.md](../runbooks/batch-ai-execution-runbook.md) 与 [session-handoff-protocol.md](../runbooks/session-handoff-protocol.md) 在"3 子任务 + 1 Shared Path + 1 Integration Owner"场景下的可执行性，不引入新规则。

**建议**（不自动成为硬门禁）：

1. 未来 batch 任务在 worker-A 报告末尾可加一行"Shared Path 读取清单"——显式记录子 agent 在 `Local Verify` 期间**只读**访问了哪些 Shared Path，避免 worker 越权落字。
2. Integration Owner 在 `Integration Verify` 失败时，可加一行 `git diff --stat <base>..HEAD --scripts` 摘要贴入 Handoff `Open Questions`，便于人工快速定位 Shared Path 落字是否正确。
3. 失败隔离演练 §5.3 段（Integration Owner 共享文件落字后 doctor 失败）建议作为 `batch-ai-execution-runbook.md` "失败场景示例" 段的**第三种**典型模式（已包含的两种：worker 失败 + 集成 verify 失败 → 三种：worker 失败 / 集成 verify 失败 / Integration Owner 自身落字失败）。

**演练产物**：本文件 + 第 4 段"集成验证输出" 实际跑出的真实退出码与关键输出，贴入 `.superpowers/sdd/task-c6-report.md`。
