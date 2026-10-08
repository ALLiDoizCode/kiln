#!/usr/bin/env bash
# Run one paid Tripo request with the trial's guards, and keep its record.
#
#   scripts/run_request.sh <name> <expected credits> <tripo arguments...>
#
# Run from learn/research/tripo-api-trial/. Example:
#   scripts/run_request.sh r1_p2_three_quarter 110 make images/crate_three_quarter.png --model tripo-p2 ...
#
# Before the request it reads the balance and refuses to run when: a STOP file exists (an earlier
# request ended in a way that needs a person); the balance is below the expected cost; or the
# credits already spent by this trial plus the expected cost would pass TRIAL_LIMIT (default 300).
# After it, it reads the balance again and appends one row to ledger.csv. If the balance fell by
# anything other than the expected cost, or the command failed, it writes STOP and exits 1.
# The model, preview.png and task.json land in models/<name>/; the command, the CLI's JSON answer
# and its messages land in requests/. The API key is never written: any tsk_ string is blanked.
set -uo pipefail
name="$1"; expected="$2"; shift 2
limit="${TRIAL_LIMIT:-300}"
mkdir -p requests models
[ -f ledger.csv ] || echo "name,started_utc,finished_utc,balance_before,balance_after,charged,expected,credits_consumed_reported,exit_code" > ledger.csv
redact() { sed -E 's/tsk_[A-Za-z0-9_-]+/tsk_REDACTED/g; s/tcli_[A-Za-z0-9_-]+/tcli_REDACTED/g'; }
balance() { tripo balance --json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(float(d["balance"]), float(d["frozen"]))'; }
if [ -f STOP ]; then echo "refused: STOP file present: $(cat STOP)"; exit 1; fi
if [ -e "models/$name" ]; then echo "refused: models/$name exists; a request is never repeated under one name"; exit 1; fi
read -r before frozen <<<"$(balance)" || { echo "refused: balance could not be read"; exit 1; }
spent=$(python3 -c 'import csv,sys; print(sum(float(r["charged"]) for r in csv.DictReader(open("ledger.csv"))))')
ok=$(python3 -c "print(int($before >= $expected and $spent + $expected <= $limit and $frozen == 0))")
if [ "$ok" != 1 ]; then
  echo "refused: balance $before (frozen $frozen), spent so far $spent, this request $expected, limit $limit"; exit 4
fi
started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "tripo $* --json --yes --no-open -o models/$name" > "requests/$name.command.txt"
tripo "$@" --json --yes --no-open -o "models/$name" 2> >(redact > "requests/$name.stderr.txt") | redact > "requests/$name.result.json"
code=${PIPESTATUS[0]}
finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for i in 1 2 3 4 5 6; do read -r after frozen <<<"$(balance)"; [ "$frozen" = "0.0" ] && break; sleep 10; done
charged=$(python3 -c "print($before - $after)")
reported=$(python3 -c 'import json,sys
try: print(json.load(open(sys.argv[1])).get("credits_consumed",""))
except Exception: print("")' "requests/$name.result.json")
echo "$name,$started,$finished,$before,$after,$charged,$expected,$reported,$code" >> ledger.csv
find "models/$name" -name task.json -exec sh -c 'sed -E "s/tsk_[A-Za-z0-9_-]+/tsk_REDACTED/g; s/tcli_[A-Za-z0-9_-]+/tcli_REDACTED/g" "$1" > "requests/$2.task.json"' _ {} "$name" \; 2>/dev/null
echo "$name: exit $code, balance $before -> $after, charged $charged (expected $expected)"
if [ "$code" != 0 ] || [ "$(python3 -c "print(int(abs($charged - $expected) < 0.005))")" != 1 ]; then
  echo "$name: exit $code, charged $charged, expected $expected, at $finished" > STOP
  echo "STOP written: look at requests/$name.* before running anything else"; exit 1
fi
