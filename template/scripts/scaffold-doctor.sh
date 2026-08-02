#!/bin/sh
# scripts/scaffold-doctor.sh — scaffold doctor (structure + links + consistency + verify)
#
# Aggregates four categories of read-only checks:
#   check_structure        AGENTS.md / Adoption Profile / docs/specs / docs/plans
#                          / ADR status / CI placeholders
#   check_links            python3 scripts/check-markdown-links.py [--template]
#   check_consistency      python3 scripts/check-governance-consistency.py [--template]
#   check_verify_profile   adopted mode only: verify entry in common manifests
#                          (pnpm/npm/yarn, uv, cargo, go, Makefile, python)
#
# Usage:
#   bash scripts/scaffold-doctor.sh [--adopted|--template] [<root>]
#       --adopted   check a target project after scaffold adoption (default)
#       --template  check this scaffold template repository
#       <root>      optional target directory; defaults to current directory
#
# Exit code:
#   0   no FAIL (warnings allowed)
#   1   at least one FAIL
#
# Output format (one line per check):
#   PASS <message>
#   WARN <message>
#   FAIL <message>
#   ...
#   Summary: N fail(s), M warning(s)

set -u

fail_count=0
warn_count=0
mode=adopted

usage() {
  printf 'Usage: bash scripts/scaffold-doctor.sh [--adopted|--template] [<root>]\n'
  printf '\n'
  printf '  --adopted   Check a target project after scaffold adoption (default).\n'
  printf '  --template  Check this scaffold template repository.\n'
  printf '  <root>      Optional target directory (default: current directory).\n'
}

pass() {
  printf 'PASS %s\n' "$1"
}

warn() {
  warn_count=$((warn_count + 1))
  printf 'WARN %s\n' "$1"
}

fail() {
  fail_count=$((fail_count + 1))
  printf 'FAIL %s\n' "$1"
}

bail() {
  printf '\nSummary: %s fail(s), %s warning(s)\n' "$fail_count" "$warn_count"
  exit 1
}

# --- parse mode flag ---
case "${1:-}" in
  ""|--adopted)
    mode=adopted
    ;;
  --template)
    mode=template
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    fail "unsupported mode: $1"
    bail
    ;;
esac

# --- parse optional positional root ---
target_root="."
if [ -n "${2:-}" ]; then
  target_root="$2"
  if [ -n "${3:-}" ]; then
    fail "too many arguments"
    bail
  fi
fi

# --- validate target root and cd into it so all relative checks resolve ---
if [ ! -d "$target_root" ]; then
  fail "target root is not a directory: $target_root"
  bail
fi

# Resolve script directory BEFORE cd so dirname("$0") stays anchored to the
# invocation cwd. CDPATH= prevents CDPATH from interfering with the subshell.
script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
checker_links="$script_dir/check-markdown-links.py"
checker_consistency="$script_dir/check-governance-consistency.py"

if ! cd "$target_root"; then
  fail "cannot enter target root: $target_root"
  bail
fi
abs_root=$(pwd)

file_contains() {
  file=$1
  pattern=$2
  [ -f "$file" ] && grep -Eq "$pattern" "$file"
}

# =========================================================================
# check_structure — AGENTS.md / Adoption Profile / L2 dirs / CI / ADR status
# =========================================================================
check_structure() {
  # Mode-conditional prefix: scaffold self uses template/ subtree;
  # adopted projects have everything at root.
  if [ "$mode" = template ]; then
    cs_prefix="template/"
  else
    cs_prefix=""
  fi

  # AGENTS.md existence + Adoption Profile placeholder fill
  if [ ! -f AGENTS.md ]; then
    fail 'AGENTS.md is missing'
  else
    pass 'AGENTS.md exists'
    if grep -Eq '<(pm|app-dir|entry-file|shared-dir|test-dir)>' AGENTS.md; then
      if [ "$mode" = template ]; then
        warn 'AGENTS.md contains Adoption Profile placeholders; allowed in template mode'
      else
        fail 'AGENTS.md still contains required Adoption Profile placeholders'
      fi
    else
      pass 'AGENTS.md required Adoption Profile placeholders are filled'
    fi
  fi

  # L2 dirs
  if [ -d docs/specs ]; then
    pass 'docs/specs exists'
  else
    fail 'docs/specs is missing'
  fi
  if [ -d docs/plans ]; then
    pass 'docs/plans exists'
  else
    fail 'docs/plans is missing'
  fi

  # CI placeholders (always WARN by design)
  found_ci=0
  for ci_file in ${cs_prefix}.github/workflows/ci.yml ${cs_prefix}.gitlab-ci.yml; do
    if [ -f "$ci_file" ]; then
      found_ci=1
      if grep -Eq '<[^>]+>' "$ci_file"; then
        if [ "$mode" = template ]; then
          warn "$ci_file contains template placeholders; allowed in template mode"
        else
          warn "$ci_file still contains angle-bracket placeholders"
        fi
      else
        pass "$ci_file has no angle-bracket placeholders"
      fi
    fi
  done
  if [ "$found_ci" -eq 0 ]; then
    warn 'no bundled CI template found'
  fi

  # ADR hard-constraint cross-reference in AGENTS.md
  missing_constraint=0
  for adr_id in ADR-0002 ADR-0003 ADR-0004 ADR-0005; do
    if ! file_contains AGENTS.md "$adr_id"; then
      missing_constraint=1
    fi
  done
  if [ "$missing_constraint" -eq 1 ]; then
    warn 'AGENTS.md does not reference all ADR-0002 through ADR-0005 hard constraints'
  fi

  # ADR status (each ADR's `## 状态` block must not be Proposed)
  for adr in \
    ${cs_prefix}docs/adr/0002-verify-hard-gate.md \
    ${cs_prefix}docs/adr/0003-multi-session-l2.md \
    ${cs_prefix}docs/adr/0004-l2-spec-and-plan.md \
    ${cs_prefix}docs/adr/0005-l3-approval-gate.md
  do
    if [ ! -f "$adr" ]; then
      fail "$adr is missing"
      continue
    fi
    status=$(awk '
      /^## 状态$/ { in_status = 1; next }
      in_status && NF { print; exit }
    ' "$adr")
    case "$status" in
      Proposed*)
        warn "$adr is Proposed while AGENTS.md treats it as a hard constraint"
        ;;
      *)
        pass "$adr status is not Proposed"
        ;;
    esac
  done
}

# =========================================================================
# check_links — delegates to python3 scripts/check-markdown-links.py
# =========================================================================
check_links() {
  if [ ! -f "$checker_links" ]; then
    warn "links checker script missing: $checker_links"
    return
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not available; skipping links check"
    return
  fi
  cl_args="--root $abs_root"
  if [ "$mode" = template ]; then
    cl_args="$cl_args --template"
  fi

  cl_out=$(python3 "$checker_links" $cl_args 2>&1)
  cl_rc=$?
  if [ "$cl_rc" -eq 0 ]; then
    pass 'no broken relative Markdown links'
    return
  fi
  if [ "$cl_rc" -eq 2 ]; then
    fail "links checker parameter error: $cl_out"
    return
  fi

  # rc == 1: emit one FAIL per non-empty finding line
  cl_emitted=0
  while IFS= read -r cl_line; do
    [ -n "$cl_line" ] || continue
    fail "broken Markdown link: $cl_line"
    cl_emitted=$((cl_emitted + 1))
  done <<EOF
$cl_out
EOF
  if [ "$cl_emitted" -eq 0 ]; then
    fail "links checker exited 1 with no findings"
  fi
}

# =========================================================================
# check_consistency — delegates to python3 scripts/check-governance-consistency.py
# =========================================================================
check_consistency() {
  if [ ! -f "$checker_consistency" ]; then
    warn "consistency checker script missing: $checker_consistency"
    return
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    warn "python3 not available; skipping consistency check"
    return
  fi
  cc_args="--root $abs_root"
  if [ "$mode" = template ]; then
    cc_args="$cc_args --template"
  fi

  cc_out=$(python3 "$checker_consistency" $cc_args 2>&1)
  cc_rc=$?
  if [ "$cc_rc" -eq 0 ]; then
    pass 'governance consistency clean'
    return
  fi
  if [ "$cc_rc" -eq 2 ]; then
    fail "consistency checker parameter error: $cc_out"
    return
  fi

  # rc == 1: emit one FAIL per non-empty GOV finding line
  cc_emitted=0
  while IFS= read -r cc_line; do
    [ -n "$cc_line" ] || continue
    fail "governance consistency: $cc_line"
    cc_emitted=$((cc_emitted + 1))
  done <<EOF
$cc_out
EOF
  if [ "$cc_emitted" -eq 0 ]; then
    fail "consistency checker exited 1 with no findings"
  fi
}

# =========================================================================
# check_verify_profile — adopted mode only
# Reads the 4 verification entry fields from AGENTS.md Adoption Profile and
# validates each one against the project's known manifests:
#   最小验证入口 (minimal) | L1 验证入口 (l1)
#   快速验证入口 (fast)    | 完整验证入口 (full)
#
# Decision per field:
#   * field row not found in AGENTS.md            → FAIL  (missing field)
#   * field value still contains <...> placeholder → WARN  (placeholder)
#   * field value is "无" / "N/A" / "不适用"     → PASS  (explicit N/A)
#   * field value resolves to an existing manifest
#     script/target (verify / test / build / lint /
#     typecheck / check)                           → PASS  (mapped)
#   * field value is a non-placeholder command but
#     no known manifest can host it                → FAIL  (unmappable)
#
# Output examples:
#   PASS  verify profile mapped to: full
#   WARN  AGENTS.md Adoption Profile field still has placeholder: 最小验证入口
#   FAIL  AGENTS.md Adoption Profile missing field: 完整验证入口
# =========================================================================
check_verify_profile() {
  cv_agents="AGENTS.md"
  if [ ! -f "$cv_agents" ]; then
    fail 'AGENTS.md is missing; cannot map verification profile'
    return
  fi

  cv_found_manifest=0
  for cv_manifest in package.json pyproject.toml Cargo.toml go.mod Makefile; do
    if [ -f "$cv_manifest" ]; then
      cv_found_manifest=1
      break
    fi
  done

  for cv_field in "最小验证入口" "L1 验证入口" "快速验证入口" "完整验证入口"; do
    # Extract the value cell of the row whose first cell equals $cv_field.
    # Note: BSD awk on macOS has a broken `==` for non-ASCII strings
    # (e.g. "字段" == "最小验证入口" returns true). We therefore avoid awk's
    # string comparison and use grep -F to locate the row, then awk -F'|' to
    # pull the trimmed value cell.
    cv_value=$(grep -F "$cv_field" "$cv_agents" \
      | head -n 1 \
      | awk -F'|' '{
          # parts[1] is empty (leading |), parts[2] is field name,
          # parts[3] is value, parts[4] is empty (trailing |).
          v = $3
          gsub(/^ +| +$/, "", v)
          print v
        }')

    if [ -z "$cv_value" ]; then
      fail "AGENTS.md Adoption Profile missing field: $cv_field"
      continue
    fi

    # Strip surrounding backticks and trailing Chinese annotation
    # (e.g. "`pnpm verify`（必填；...）" → "pnpm verify").
    cv_cmd=$(printf '%s' "$cv_value" | sed 's/`//g' | sed 's/（.*//' | sed 's/[[:space:]]*$//')

    # Placeholder check: <...> still present after stripping
    if printf '%s' "$cv_cmd" | grep -Eq '<[^>]+>'; then
      warn "AGENTS.md Adoption Profile field still has placeholder: $cv_field"
      continue
    fi

    # Explicit N/A: "无" / "N/A" / "不适用"
    case "$cv_cmd" in
      无|N/A|不适用)
        pass "verify profile entry marked as not applicable: $cv_field"
        continue
        ;;
    esac

    # No manifest at all → cannot reliably host a verify entry
    if [ "$cv_found_manifest" -eq 0 ]; then
      fail "AGENTS.md Adoption Profile field command not found in any manifest: $cv_field"
      continue
    fi

    # Try to map the command to a known manifest entry.
    # The command must reference a standard action that the manifest exposes.
    cv_mapped=0
    cv_cmd_pre='(^|[ /])'
    cv_cmd_post='([ /]|$)'
    cv_man_pre='(^|["._ -])'
    cv_man_post='([":._ -]|$)'
    for cv_key in verify test build lint typecheck check; do
      if printf '%s' "$cv_cmd" | grep -Eq "${cv_cmd_pre}${cv_key}${cv_cmd_post}"; then
        for cv_manifest in package.json pyproject.toml Cargo.toml go.mod Makefile; do
          if [ -f "$cv_manifest" ] && grep -Eq "${cv_man_pre}${cv_key}${cv_man_post}" "$cv_manifest"; then
            cv_mapped=1
            break 2
          fi
        done
      fi
    done

    if [ "$cv_mapped" -eq 1 ]; then
      pass "verify profile mapped to: $cv_field"
    else
      fail "AGENTS.md Adoption Profile field command not found in any manifest: $cv_field"
    fi
  done
}

# =========================================================================
# print_summary — emit the Summary line and set return code based on FAIL count
# =========================================================================
print_summary() {
  printf '\nSummary: %s fail(s), %s warning(s)\n' "$fail_count" "$warn_count"
  if [ "$fail_count" -gt 0 ]; then
    return 1
  fi
  return 0
}

# --- run all checks ---
check_structure
check_links
check_consistency
if [ "$mode" = adopted ]; then
  check_verify_profile
fi

print_summary
exit $?
