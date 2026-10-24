"""Score the review-eval runs against the pre-registered key and write ops/evals/results.csv.

Verdicts were assigned by a human-in-the-loop reading of runs/*.md (see ops/evals/ground-truth.md,
sha256 da5b610e...). Only exceptions to the "expected" outcome are listed below.
Usage: python3 scripts/eval_report.py
"""
import csv
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFECTIVE = ["case-01", "case-02", "case-03", "case-05", "case-07", "case-08", "case-09", "case-10", "case-11"]
CLEAN = ["case-04", "case-06", "case-12"]
ALL_CASES = [f"case-{n:02d}" for n in range(1, 13)]

# (prompt, run, case) -> (verdict, note). Anything not listed is caught / clean_ok.
EXCEPTIONS = {
    ("v1", 1, "case-09"): ("missed", "reviewer did not notice README reset claim is false"),
    ("v1", 3, "case-06"): ("false_alarm", "asserted clock-adjustment test flakiness as a defect"),
    ("v2", 2, "case-09"): ("missed", "'No defects found' despite v2 instruction to test doc claims"),
    ("v2", 3, "case-09"): ("missed", "'No defects found' despite v2 instruction to test doc claims"),
}
NOTES = {
    ("v1", 3, "case-09"): "caught at medium confidence",
    ("v1", 2, "case-09"): "caught via 'contradicts / will not reset'",
}


def wilson(successes, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def build_rows():
    rows = []
    for prompt, label in (("v1", "baseline"), ("v2", "variant")):
        for run in (1, 2, 3):
            for case in ALL_CASES:
                default = "caught" if case in DEFECTIVE else "clean_ok"
                verdict, note = EXCEPTIONS.get((prompt, run, case), (default, NOTES.get((prompt, run, case), "")))
                rows.append({
                    "run": f"{label}-{run}", "case": case, "model": "default (not exposed to harness)",
                    "prompt_version": prompt, "verdict": verdict,
                    "finding_summary": f"see ops/evals/runs/{label}-run{run}.md",
                    "confidence_reported": "see raw file", "notes": note,
                })
    return rows


def summarise(rows, prompt, treat_09_as_clean=False):
    subset = [r for r in rows if r["prompt_version"] == prompt]
    caught = missed = false_alarm = clean_ok = 0
    for r in subset:
        if treat_09_as_clean and r["case"] == "case-09":
            if r["verdict"] == "caught":
                false_alarm += 1
            else:
                clean_ok += 1
            continue
        caught += r["verdict"] == "caught"
        missed += r["verdict"] == "missed"
        false_alarm += r["verdict"] == "false_alarm"
        clean_ok += r["verdict"] == "clean_ok"
    return caught, missed, false_alarm, clean_ok


def fmt(successes, n):
    low, high = wilson(successes, n)
    return f"{successes}/{n} = {successes / n:.0%} (95% Wilson CI {low:.0%}-{high:.0%})"


def main():
    rows = build_rows()
    out = ROOT / "ops/evals/results.csv"
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out.relative_to(ROOT)} ({len(rows)} rows)\n")

    for prompt in ("v1", "v2"):
        caught, missed, false_alarm, clean_ok = summarise(rows, prompt)
        print(f"== prompt {prompt} (primary key: 9 defective, 3 clean, 3 runs) ==")
        print("  caught      ", fmt(caught, caught + missed))
        print("  missed      ", fmt(missed, caught + missed))
        print("  false alarm ", fmt(false_alarm, false_alarm + clean_ok))
        caught, missed, false_alarm, clean_ok = summarise(rows, prompt, treat_09_as_clean=True)
        print("  sensitivity, case-09 treated as clean:")
        print("    caught (8 defective)", fmt(caught, caught + missed))
        print("    false alarm        ", fmt(false_alarm, false_alarm + clean_ok))
        print()


if __name__ == "__main__":
    main()
