# Deliverable 4 - Review-agent evaluation

Reproduce the numbers: `python3 scripts/eval_report.py` (writes `ops/evals/results.csv`, 72 rows).

## Setup (what was actually run)

- Reviewer: a fresh `explore` sub-agent session per (run, case), told to read only its one diff. The model is the
  tool default; the harness does not expose the model ID, so it is **not recorded** (and was held constant).
  The sessions inherit repo instructions (`AGENTS.md`), a constant confound.
- Cases: the 10 original `ops/evals/cases/case-01..10.diff` (untouched) plus two added in
  `ops/evals/cases-added/`:
  - `case-11` (defective): INC-2041 deploy diff - per-call `HttpClient` plus synchronous PayEx call after approval
    (real incident; SocketException 10048 in the logs).
  - `case-12` (clean): real starter commit 3834913 (.gitignore, AGENTS.md doc lines, coverlet package).
- Ground truth was written **before any review ran**: `ops/evals/ground-truth.md`,
  sha256 `da5b610e0318ce7269fd886203c4e6a625c6123387ff317df512da630b821a34`
  (created 2026-10-24T14:57:58Z). 9 defective (01, 02, 03, 05, 07, 08, 09, 10, 11), 3 clean (04, 06, 12).
- Scoring: done by the AI assistant (the same model family as the reviewers), not independently, and not blind
  to which prompt produced an output. The user should spot-check `runs/*.md` against `results.csv`.
  "Caught" = the planted defect was named. "False alarm" = a defect asserted on a clean case (style or naming
  remarks do not count). Extra valid findings on defective cases are not counted either way.
- Baseline: prompt v1 = the prompt in `ops/evals/README.md`, 3 runs x 12 cases (raw: `runs/baseline-run{1,2,3}.md`).
- The single changed variable: prompt v2 = v1 + "Only report a defect if you can describe a concrete input or
  sequence of events that triggers it and its observable consequence; do not report hypothetical, stylistic or
  test-flakiness concerns. Treat claims in documentation and comments as testable statements and check whether
  the code around them supports them." Nothing else changed. 3 runs x 12 cases (`runs/variant-run{1,2,3}.md`).
- Hypothesis (recorded before v2 ran): v2 reduces false alarms (1/9 -> 0/9) without lowering recall, and may
  make case-09 more reliable.

## Results

| Prompt | Caught (defective, n=27) | Missed | False alarms (clean, n=9) |
|---|---|---|---|
| v1 baseline | 26/27 = 96% (CI 82-99%) | 1/27 = 4% | 1/9 = 11% (CI 2-44%) |
| v2 variant | 25/27 = 93% (CI 77-98%) | 2/27 = 7% | 0/9 = 0% (CI 0-30%) |

Per run: v1 caught 8, 9, 9 of 9; false alarms 0, 0, 1 of 3. v2 caught 9, 8, 8 of 9; false alarms 0, 0, 0 of 3.
Intervals are 95% Wilson.

Where the differences come from:
- v1 miss: run 1 case-09. v1 false alarm: run 3 case-06 (a clock-adjustment flakiness claim; a lenient reader
  might call it style, I scored it strictly as a false alarm).
- v2 misses: runs 2 and 3, both case-09 ("No defects found"), even though the v2 text explicitly asks to test
  documentation claims. Run 1 did catch it.
- Case-11 was caught in all 6 runs, and the reviewers also found the sync-call/no-idempotency and
  DecisionResponse-rename issues.

Sensitivity to the case-09 key. Case-09 is a README claim ("sign out and in to reset the data"); the
repository is a singleton so sign-out does not reset data. I judge it defective, but it is the least certain key
entry. If it is treated as clean: both prompts catch 24/24 other defects, and false alarms become v1 3/12 (25%)
vs v2 1/12 (8%). The headline conclusion depends on this one case.

## Did the change improve things?

**Not demonstrably.** v2 moved false alarms from 1 to 0 and recall from 26 to 25 caught. Each difference is a
single observation, and the intervals overlap almost completely (false alarms 2-44% vs 0-30%; recall 82-99% vs
77-98%). The data is consistent with no effect, a small false-alarm benefit, or a small recall cost. v2 did not
make case-09 more reliable (caught 1/3 vs 2/3 for v1), which contradicts that part of the hypothesis.

## Confidence at this sample size

Low. 12 cases, 3 runs, 9 clean observations. Repeat runs re-test the same 12 diffs, so the effective sample is
closer to 12 than 36. A ceiling effect (v1 already ~96%) leaves little room to show improvement. Telling 11% from
0% false alarms would need on the order of 100+ clean observations. One scorer, one model, no blinding. Many
diffs are textbook defects (SQL injection, missing authorization) a model has likely seen, so a real diff set
would likely score lower.

## Recommendation

Keep v1 for now; the evidence does not justify switching. If v2 is wanted, re-test it on more clean diffs from the
real history and on subtler defects, and change doc-claim checking (case-09 style) as a separate variable so the
effects are not mixed.

Note: several eval diffs reference symbols that do not exist in this tree (`CurrentUser`, `DecisionResponse`,
`_queries`), so reviewers judge self-contained diffs, not this codebase.

## Audit re-check (2026-10-24)

- `python3 scripts/eval_report.py` reproduces every figure in the Results table and the case-09 sensitivity
  numbers (v1 26/27, 1/9; v2 25/27, 0/9; sensitivity 24/24, 3/12 and 1/12).
- I re-read all six `runs/*.md` files against the verdicts. They match, but note how the CSV is produced:
  `scripts/eval_report.py` hard-codes the four exceptions (v1 run 1 case-09, v1 run 3 case-06, v2 runs 2 and 3
  case-09) and defaults every other row to caught/clean_ok. It does not parse the run files, so the CSV is only as
  correct as that hand-entered list and my reading. `finding_summary` is a pointer, not a summary.
- The Wilson intervals treat the 27 (and 9) observations as independent. They are repeats of 9 (and 3) diffs, so
  the true uncertainty is wider than shown; read the intervals as optimistic.
- The ground-truth hash matches the file (`sha256sum`). The creation timestamp and the claim that it preceded the
  reviews are the submitter's statement; git cannot confirm it because the file was first committed together with
  the run outputs.
- Proxies/assumptions: the case diffs for 01-10 are the provided starter diffs, and several reference code absent
  from this tree; case-11 is derived from the INC-2041 pack, whose incident data is invented (`ops/README.md`).
  "Model: default" is not an identified model. `variant-run1.md` originally pointed to a nonexistent
  `../README-assignment.md`; it now points to this report.
