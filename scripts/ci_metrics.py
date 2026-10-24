"""Compute two metrics from ops/pipeline/run-timings.csv.

CAVEAT: this file describes the *planned* pipeline in ops/pipeline/ci-pipeline.yml (it has docker/health steps
that do not exist in the real .github/workflows/ci.yml). The numbers are therefore proxies from provided
workshop data, not measurements of this repository's real CI.
Usage: python3 scripts/ci_metrics.py
"""
import csv
import pathlib
import statistics
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
runs = defaultdict(lambda: {"seconds": 0, "conclusion": set(), "event": None, "branch": None, "started": None})

with (ROOT / "ops/pipeline/run-timings.csv").open() as handle:
    for row in csv.DictReader(handle):
        run = runs[int(row["run_number"])]
        run["seconds"] += int(row["duration_seconds"])
        run["conclusion"].add(row["conclusion"])
        run["event"] = row["event"]
        run["branch"] = row["branch"]
        run["started"] = row["started_at"]

durations = [run["seconds"] for run in runs.values()]
failed = [number for number, run in runs.items() if run["conclusion"] != {"success"}]

print(f"runs: {len(runs)}  ({min(runs)}..{max(runs)}), dates {min(r['started'] for r in runs.values())[:10]}"
      f" to {max(r['started'] for r in runs.values())[:10]}")
print(f"metric 1 - CI duration per run: median {statistics.median(durations) / 60:.1f} min, "
      f"mean {statistics.mean(durations) / 60:.1f} min, min {min(durations) / 60:.1f}, max {max(durations) / 60:.1f}")
print(f"metric 2 - CI failure rate: {len(failed)}/{len(runs)} = {len(failed) / len(runs):.0%}; failed runs {failed}")
for event in sorted({run["event"] for run in runs.values()}):
    subset = [number for number, run in runs.items() if run["event"] == event]
    bad = [number for number in subset if number in failed]
    print(f"  event={event}: {len(bad)}/{len(subset)} failed")
