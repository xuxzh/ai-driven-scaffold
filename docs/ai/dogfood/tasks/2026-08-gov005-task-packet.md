# GOV005 ADR 索引一致性任务包

## 目标

- 为 `scripts/check-governance-consistency.py` 增加 GOV005，确保 `docs/adr/README.md` 索引集合与同目录实际 ADR Markdown 文件集合完全一致。

## 级别

- L1：单一检查规则，沿用现有 checker CLI / 输出架构，仅改一个生产文件、一个测试文件和本任务包。

## 锚点

- `scripts/check-governance-consistency.py`：`iter_check_lines`、规则实现区、`main`
- `scripts/tests/test_check_governance_consistency.py`：规则级 tempfile mini-repo 测试
- `docs/adr/README.md`：被检查的 ADR 索引

## 假设

- 若分别提取 `docs/adr/` 直接子目录中匹配 `NNNN-<name>.md` 的实际文件名集合，以及 README 中同目录 Markdown 链接目标里匹配该格式的文件名集合，则集合不等或 README 缺失时 GOV005 必定产生 finding；集合相等时不产生 GOV005 finding。

## 最小改动

- 添加聚焦测试，覆盖 README 缺失、漏索引、悬空索引和集合匹配。
- 添加一个 GOV005 检查函数并接入现有 findings 汇总；更新模块/规则说明到 GOV001–GOV005。
- 不引入依赖，不改变现有退出码和单行 finding 格式。

## 验证

- `python3 scripts/tests/test_check_governance_consistency.py`：测试先因缺少 GOV005 行为出现预期 RED，实施后全部通过。
- `python3 scripts/check-governance-consistency.py --root . --template`：退出码 0。
- `git diff --check -- scripts/check-governance-consistency.py scripts/tests/test_check_governance_consistency.py docs/ai/dogfood/tasks/2026-08-gov005-task-packet.md`：退出码 0。

## 非目标

- 不修改 `scripts/scaffold-doctor.sh`、CI、Plan A/B、父 Plan C 或任何 Owned paths 之外文件。
- 不重构 GOV001–GOV004，不新增第三方依赖，不提交或暂存改动。

## 后续升级触发条件

- 若准确解析目标需要完整 Markdown parser、跨目录索引、改变 CLI/output contract，或改动超过现有单 checker 架构，则升级到 L2 spec + plan；本任务不实施这些扩展。

## 批量子字段

- Owner: 不适用（单 agent 串行）
- Owned Paths: 不适用（单 agent 串行；范围由 brief 的 Owned paths 固定）
- Shared Paths: 不适用（单 agent 串行）
- Prohibited Paths: 不适用（单 agent 串行；禁区由 brief 固定）
- Depends On: 不适用（单 agent 串行）
- Local Verify: 不适用（单 agent 串行；精确命令见“验证”）
- Integration Owner: 不适用（单 agent 串行）
- Integration Verify: 不适用（单 agent 串行）

## 验证证据（实施完成后必填）

| 命令 | 退出码 | 关键输出 | 备注 |
|---|---:|---|---|
| `python3 scripts/tests/test_check_governance_consistency.py`（RED） | 1 | `Ran 17 tests in 0.462s`；`FAILED (failures=3)`；三个 GOV005 缺失行为断言均为 `AssertionError: 0 != 1` | 预期 RED；非语法或 fixture setup 错误 |
| `python3 scripts/tests/test_check_governance_consistency.py`（GREEN） | 0 | `Ran 17 tests in 0.539s`；`OK` | 全部通过 |
| `python3 scripts/check-governance-consistency.py --root . --template` | 0 | `(no output)` | 仓库实际 ADR 集合与索引匹配 |
| `git diff --check -- scripts/check-governance-consistency.py scripts/tests/test_check_governance_consistency.py docs/ai/dogfood/tasks/2026-08-gov005-task-packet.md` | 0 | `(no output)` | 无 whitespace error |

未跑项：无。
