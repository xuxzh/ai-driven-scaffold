#!/usr/bin/env bash
# scripts/tests/scaffold-doctor-test.sh
#
# Integration tests for scripts/scaffold-doctor.sh using mktemp -d fixtures.
# Covers 6 scenarios (L1+ governance gate):
#
#   1. missing required files (no AGENTS.md / docs/specs / docs/plans)         -> FAIL
#   2. missing manifest verify entry (--adopted)                               -> FAIL
#   3. has manifest verify entry (--adopted)                                   -> PASS (0 fail)
#   4. template mode + CI file with <...> placeholders                         -> WARN, not FAIL
#   5. template mode + no manifest                                              -> WARN, not FAIL
#   6. real scaffold repo --template                                            -> 0 fail
#
# Each scenario asserts:
#   * FAIL count matches (eq:N or ge:N)
#   * exit code matches (eq:0 or ne:0)
#   * WARN count is informational; we only assert >= 1 when the scenario
#     specifically exercises a warning path.

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCTOR="$REPO_ROOT/scripts/scaffold-doctor.sh"

PASS_COUNT=0
FAIL_TOTAL=0

record_pass() {
  printf '  PASS  %s\n' "$1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

record_fail() {
  printf '  FAIL  %s\n' "$1"
  FAIL_TOTAL=$((FAIL_TOTAL + 1))
}

# Count PASS/WARN/FAIL lines via awk; emit "p w f" on stdout.
count_pwf() {
  awk '
    /^PASS / { p++ }
    /^WARN / { w++ }
    /^FAIL / { f++ }
    END { print (p ? p : 0), (w ? w : 0), (f ? f : 0) }
  '
}

# Build the canonical structured fixture: AGENTS.md + docs/specs + docs/plans +
# docs/adr/0002..0005 stubs + docs/adr/README.md 索引（含全部 ADR 文件名）。
# GOV005 要求 docs/adr/README.md 存在并与同目录 ADR 文件名集合一致；
# 各 scenario 默认走此结构，单文件缺失型 scenario 会复用此 fixture
# 并在 run_scenario 之前删除对应文件。
# $2 是可选 prefix；template mode 下用 "template/" 把下发物放到
# template/ 子树下，以匹配 doctor 的 mode-conditional 路径。
# docs/specs 与 docs/plans 是脚手架自身 L2 目录，两种 mode 都在根，不加 prefix。
make_structured_root() {
  local root="$1"
  local prefix="${2:-}"
  mkdir -p "$root/docs/specs" "$root/docs/plans" "$root/${prefix}docs/adr"
  printf '# Stub\n' > "$root/AGENTS.md"
  for adr in 0002-verify-hard-gate.md 0003-multi-session-l2.md \
             0004-l2-spec-and-plan.md 0005-l3-approval-gate.md; do
    cat > "$root/${prefix}docs/adr/$adr" <<'EOF'
# Stub ADR

## 状态

Accepted
EOF
  done
  cat > "$root/${prefix}docs/adr/README.md" <<'EOF'
# ADR 索引

- [0002 verify](0002-verify-hard-gate.md)
- [0003 sessions](0003-multi-session-l2.md)
- [0004 spec+plan](0004-l2-spec-and-plan.md)
- [0005 L3 approval](0005-l3-approval-gate.md)
EOF
}

# Track the latest temp dir so a safety-net trap can clean up.
TMPDIR_LATEST=""
cleanup_tmp() {
  if [ -n "$TMPDIR_LATEST" ] && [ -d "$TMPDIR_LATEST" ]; then
    rm -rf "$TMPDIR_LATEST"
  fi
}

# Reusable scenario runner.
#   $1  label           (used in test messages)
#   $2  fail expectation (eq:N | ge:N)
#   $3  warn expectation (any | eq:N | ge:N)
#   $4  exit expectation (eq:0 | ne:0)
#   $5  doctor mode     ("--adopted" or "--template")
#   $6  doctor root     (path; empty = use default cwd)
run_scenario() {
  local label="$1" fcheck="$2" wcheck="$3" echeck="$4" mode="$5" root="$6"
  local output exit_code p w f
  if [ -n "$root" ]; then
    output=$(bash "$DOCTOR" "$mode" "$root" 2>&1)
  else
    output=$(bash "$DOCTOR" "$mode" 2>&1)
  fi
  exit_code=$?
  read -r p w f < <(printf '%s\n' "$output" | count_pwf)

  local ok=1
  case "$fcheck" in
    eq:*) [ "$f" -eq "${fcheck#eq:}" ] || ok=0 ;;
    ge:*) [ "$f" -ge "${fcheck#ge:}" ] || ok=0 ;;
    *) ok=0 ;;
  esac
  case "$wcheck" in
    any) ;;
    eq:*) [ "$w" -eq "${wcheck#eq:}" ] || ok=0 ;;
    ge:*) [ "$w" -ge "${wcheck#ge:}" ] || ok=0 ;;
    *) ok=0 ;;
  esac
  case "$echeck" in
    eq:0) [ "$exit_code" -eq 0 ] || ok=0 ;;
    ne:0) [ "$exit_code" -ne 0 ] || ok=0 ;;
    *) ok=0 ;;
  esac

  if [ "$ok" -eq 1 ]; then
    record_pass "$label -> p=$p w=$w f=$f exit=$exit_code"
  else
    record_fail "$label: expected f=$fcheck w=$wcheck exit=$echeck; got p=$p w=$w f=$f exit=$exit_code"
    printf '   output (head):\n'
    printf '%s\n' "$output" | sed 's/^/     /'
  fi
}

# ---------------- Scenario 1 ----------------
echo "[Scenario 1] missing required files (no AGENTS.md / docs/specs / docs/plans) -> FAIL"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
run_scenario "missing-files"    ge:1 any ne:0 --adopted  "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 2 ----------------
echo "[Scenario 2] missing manifest verify entry (--adopted) -> FAIL"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
make_structured_root "$TMPDIR_LATEST"
printf '{"name":"x","scripts":{"test":"echo ok"}}\n' > "$TMPDIR_LATEST/package.json"
run_scenario "missing-verify"   ge:1 any ne:0 --adopted  "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 3 ----------------
echo "[Scenario 3] has manifest verify entry (--adopted) -> PASS (0 fail)"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
make_structured_root "$TMPDIR_LATEST"
cat > "$TMPDIR_LATEST/AGENTS.md" <<'EOF'
# Stub

| 字段 | 本仓库值 |
|---|---|
| 包管理器 | pnpm |
| 主要应用目录 | `src/` |
| 入口代码锚点 | `index.ts` |
| 共享包目录 | 无 |
| 测试目录 | `tests/` |
| 最小验证入口 | `pnpm verify` |
| L1 验证入口 | `pnpm verify` |
| 快速验证入口 | `pnpm verify` |
| 完整验证入口 | `pnpm verify` |
EOF
printf '{"name":"x","scripts":{"test":"echo ok","verify":"bash scripts/scaffold-doctor.sh"}}\n' > "$TMPDIR_LATEST/package.json"
run_scenario "present-verify"   eq:0 any eq:0 --adopted  "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 4 ----------------
echo "[Scenario 4] template mode CI file with <...> placeholders -> WARN, not FAIL"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
make_structured_root "$TMPDIR_LATEST" "template/"
mkdir -p "$TMPDIR_LATEST/template/.github/workflows"
cat > "$TMPDIR_LATEST/AGENTS.md" <<'EOF'
# Stub

| pm | <pm> |
| app-dir | <app-dir> |
| entry-file | <entry-file> |
| shared-dir | <shared-dir> |
| test-dir | <test-dir> |
EOF
cat > "$TMPDIR_LATEST/template/.github/workflows/ci.yml" <<'EOF'
name: ci
jobs:
  build:
    steps:
      - run: <command>
EOF
run_scenario "template-ci-warn" eq:0 ge:1 eq:0 --template "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 5 ----------------
echo "[Scenario 5] template mode no manifest -> WARN, not FAIL"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
make_structured_root "$TMPDIR_LATEST" "template/"
cat > "$TMPDIR_LATEST/AGENTS.md" <<'EOF'
# Stub

| pm | <pm> |
| app-dir | <app-dir> |
| entry-file | <entry-file> |
| shared-dir | <shared-dir> |
| test-dir | <test-dir> |
EOF
run_scenario "template-no-manifest" eq:0 ge:1 eq:0 --template "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 6 ----------------
echo "[Scenario 6] real scaffold repo --template -> 0 fail"
run_scenario "real-repo-template" eq:0 any eq:0 --template ""

# ---------------- Scenario 7 ----------------
echo "[Scenario 7] adopted mode AGENTS.md missing 4 verify entry fields -> FAIL"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
make_structured_root "$TMPDIR_LATEST"
cat > "$TMPDIR_LATEST/AGENTS.md" <<'EOF'
# Stub

| 字段 | 本仓库值 |
|---|---|
| 包管理器 | pnpm |
| 主要应用目录 | `docs/` |
| 入口代码锚点 | 无 |
| 共享包目录 | 无 |
| 测试目录 | 无 |
EOF
printf '{"name":"x","scripts":{"test":"echo ok","verify":"echo ok"}}\n' > "$TMPDIR_LATEST/package.json"
run_scenario "adopted-missing-4-fields" ge:1 any ne:0 --adopted "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Scenario 8 ----------------
echo "[Scenario 8] adopted mode AGENTS.md 4 fields present but contain <...> placeholders -> WARN"
TMPDIR_LATEST=$(mktemp -d)
trap 'cleanup_tmp' EXIT INT TERM
make_structured_root "$TMPDIR_LATEST"
cat > "$TMPDIR_LATEST/AGENTS.md" <<'EOF'
# Stub

| 字段 | 本仓库值 |
|---|---|
| 包管理器 | pnpm |
| 主要应用目录 | `docs/` |
| 入口代码锚点 | 无 |
| 共享包目录 | 无 |
| 测试目录 | 无 |
| 最小验证入口 | `<command>` |
| L1 验证入口 | `<command>` |
| 快速验证入口 | `<command>` |
| 完整验证入口 | `<command>` |
EOF
printf '{"name":"x","scripts":{"test":"echo ok","verify":"echo ok"}}\n' > "$TMPDIR_LATEST/package.json"
run_scenario "adopted-placeholder-4-fields" ge:0 ge:1 eq:0 --adopted "$TMPDIR_LATEST"
cleanup_tmp
trap - EXIT INT TERM
TMPDIR_LATEST=""

# ---------------- Summary ----------------
echo ""
echo "=== Test Summary ==="
echo "Passed: $PASS_COUNT / 8"
echo "Failed: $FAIL_TOTAL / 8"
if [ "$FAIL_TOTAL" -eq 0 ]; then
  exit 0
else
  exit 1
fi
