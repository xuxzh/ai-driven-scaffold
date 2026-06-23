#!/bin/sh

set -u

fail_count=0
warn_count=0
mode=adopted

usage() {
  printf 'Usage: bash scripts/scaffold-doctor.sh [--adopted|--template]\n'
  printf '\n'
  printf '  --adopted   Check a target project after scaffold adoption (default).\n'
  printf '  --template  Check this scaffold template repository.\n'
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
    usage
    fail "unsupported mode: $1"
    printf '\nSummary: %s fail(s), %s warning(s)\n' "$fail_count" "$warn_count"
    exit 1
    ;;
esac

if [ "${2:-}" ]; then
  usage
  fail "too many arguments"
  printf '\nSummary: %s fail(s), %s warning(s)\n' "$fail_count" "$warn_count"
  exit 1
fi

file_contains() {
  file=$1
  pattern=$2

  [ -f "$file" ] && grep -Eq "$pattern" "$file"
}

check_agents_md() {
  if [ ! -f AGENTS.md ]; then
    fail 'AGENTS.md is missing'
    return
  fi

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
}

check_l2_dirs() {
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
}

check_verify_entry() {
  found_manifest=0
  found_verify=0

  for manifest in package.json pyproject.toml Cargo.toml go.mod mix.exs Makefile justfile Taskfile.yml Taskfile.yaml; do
    if [ -f "$manifest" ]; then
      found_manifest=1
      if grep -Eq '(^|["._ -])verify([":._ -]|$)' "$manifest"; then
        found_verify=1
      fi
    fi
  done

  if [ "$found_manifest" -eq 0 ]; then
    warn 'no common project manifest found; verify entry could not be detected'
    return
  fi

  if [ "$found_verify" -eq 1 ]; then
    pass 'verify entry detected in a common manifest'
  else
    fail 'no verify entry detected in common manifests'
  fi
}

check_ci_placeholders() {
  found_ci=0

  for ci_file in .github/workflows/ci.yml .gitlab-ci.yml; do
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
}

check_adr_status() {
  missing_constraint=0

  for adr_id in ADR-0002 ADR-0003 ADR-0004 ADR-0005; do
    if ! file_contains AGENTS.md "$adr_id"; then
      missing_constraint=1
    fi
  done

  if [ "$missing_constraint" -eq 1 ]; then
    warn 'AGENTS.md does not reference all ADR-0002 through ADR-0005 hard constraints'
  fi

  for adr in \
    docs/adr/0002-verify-hard-gate.md \
    docs/adr/0003-multi-session-l2.md \
    docs/adr/0004-l2-spec-and-plan.md \
    docs/adr/0005-l3-approval-gate.md
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

check_agents_md
check_l2_dirs
check_verify_entry
check_ci_placeholders
check_adr_status

printf '\nSummary: %s fail(s), %s warning(s)\n' "$fail_count" "$warn_count"

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi

exit 0
