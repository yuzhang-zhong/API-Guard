#!/usr/bin/env bash
# Run only in an ephemeral CI runner under dbus-run-session, never on a user keyring.
set -euo pipefail
: "${API_GUARD_ISOLATED_TEST:?Set only inside an isolated CI test environment}"
export XDG_DATA_HOME="$(mktemp -d)"
trap 'rm -rf "$XDG_DATA_HOME"' EXIT
printf 'synthetic-ci-keyring-password\n' | gnome-keyring-daemon --unlock --components=secrets >/dev/null
python_cmd=(python api-guardian/scripts/api_guard.py)
printf 'SYNTHETIC-NOT-A-REAL-CREDENTIAL' | "${python_cmd[@]}" store api-guard-ci --stdin
actual="$("${python_cmd[@]}" get api-guard-ci --reveal)"
[[ "$actual" == 'SYNTHETIC-NOT-A-REAL-CREDENTIAL' ]]
"${python_cmd[@]}" delete api-guard-ci
if "${python_cmd[@]}" get api-guard-ci >/dev/null 2>&1; then
  echo 'Deleted synthetic item is unexpectedly still readable' >&2
  exit 1
fi
# A broken bus must fail, not claim success. No real keyring is reachable.
if DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/api-guard-no-such-bus "${python_cmd[@]}" delete api-guard-ci > /tmp/delete-out.txt 2>/tmp/delete-err.txt; then
  echo 'Backend failure incorrectly reported as success' >&2
  exit 1
fi
[[ ! -s /tmp/delete-out.txt ]]
grep -q 'did not confirm credential deletion' /tmp/delete-err.txt
echo 'Isolated Linux store / retrieve / delete / failure checks passed.'
