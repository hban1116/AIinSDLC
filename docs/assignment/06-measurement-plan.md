# Deliverable 6 - Measurement plan

Three metrics are in scope: lead time, change failure rate, review turnaround. Two numbers are actually captured
below; they are **proxies** and are labelled as such. Nothing here is a measurement of production.

## What I could capture now

Command: `python3 scripts/ci_metrics.py` (reads `ops/pipeline/run-timings.csv`, 20 runs, 2026-01-19 to 2026-02-02).

| # | Number | Value | What it is a proxy for | Source |
|---|---|---|---|---|
| 1 | CI duration per run (sum of step durations) | median **31.3 min** (mean 31.3, range 28.4-35.1) | the build/verify slice of lead time | `ops/pipeline/run-timings.csv` |
| 2 | CI failure rate | **2/20 = 10%** (runs 6, 14); 2/12 on pull requests, 0/8 on pushes | an early-warning proxy for change failure rate | same file |

Honest limits:
- The CSV describes the **planned** pipeline in `ops/pipeline/ci-pipeline.yml` (docker build, health check). The real
  `.github/workflows/ci.yml` is only build + test, and `ops/README.md` says the data is invented. These numbers
  say nothing about this repository's real pipeline speed.
- A failed CI run is not a change failure. Change failure rate (DORA) counts changes that reach production and
  then need a fix, rollback or hotfix. There is no production, so this is a different quantity.
- 20 runs over two weeks, no confidence interval worth quoting; 2 failures is too few to see a trend.
- Real git history has 6 commits (5 on 2026-10-05, 1 on 2026-10-12), no PRs, no deploys. Lead time and review
  turnaround cannot be computed from it. I did not compute commit-gap "lead time" because it would be meaningless.

## Plan for the real baselines

| Metric | Definition | Exact source | Query / method |
|---|---|---|---|
| Lead time for changes | first commit on a PR branch to the deploy of the merge commit | GitHub PR + Actions deployment data | `gh pr list --state merged --json number,createdAt,mergedAt,commits` for first-commit time; deploy completion time from the deploy workflow run (`gh run list --workflow deploy.yml --json headSha,conclusion,updatedAt`), joined on merge commit SHA. Report median and p85 weekly. |
| Change failure rate | deploys followed by a rollback, hotfix, or incident within 7 days / all deploys | deploy runs + incident tickets (INC-xxxx) + commits labelled `hotfix`/`revert` | Count deploys in the window; count those whose SHA is linked to an incident or reverted within 7 days. Needs a rule that every incident records the offending SHA - that field does not exist yet. |
| Review turnaround | PR marked ready for review to first human review | GitHub PR timeline | `gh api repos/{owner}/{repo}/pulls/{n}/reviews` first non-author `submitted_at` minus the `ready_for_review` event time from `/issues/{n}/timeline`. Exclude agent reviews so the AI reviewer does not flatter the number. |

Prerequisites: a PR-based workflow on the submission repo with at least a few weeks of merged PRs, a deploy
workflow or release tag to anchor "deployed", and an incident-to-SHA record. None of these exist today (and no
`gh` CLI is installed in this environment; the GitHub MCP tools could be used instead with the owner's access).

## Using the numbers to judge the AI changes

Decision rule to agree before rollout: compare the 4 weeks before and after adopting the review agent, with
review turnaround and change failure rate as the primary pair and lead time as the guard. With a team of 6 the
weekly counts are small, so read medians over at least 8 weeks and expect wide uncertainty; do not claim an
effect from fewer than ~30 merged PRs per period.
