#!/usr/bin/env bash
# memrun.sh <log> <cmd...>: run cmd, print its peak resident memory (MiB, whole process tree) and seconds.
log="$1"; shift
"$@" > "$log" 2>&1 &
pid=$!; peak=0; minavail=999999; SECONDS=0
while kill -0 $pid 2>/dev/null; do
  r=0; for p in $pid $(pgrep -P $pid); do v=$(awk '/VmRSS/{print int($2/1024)}' /proc/$p/status 2>/dev/null); r=$((r+${v:-0})); done
  [ $r -gt $peak ] && peak=$r
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -lt $minavail ] && minavail=$a
  if [ $a -lt 1500 ]; then echo "STOPPED: under 1.5 GB of memory left"; kill $pid; fi
  sleep 0.5
done
wait $pid; rc=$?
echo "exit=$rc peak_rss_mib=$peak min_ram_available_mib=$minavail seconds=$SECONDS"
