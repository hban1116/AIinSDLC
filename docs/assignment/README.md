# Assignment submission - index and checklist

Branch: `assignment/submission` (starter history preserved underneath). Status as of 2026-10-24.

| # | Deliverable | Status | Evidence |
|---|---|---|---|
| 1a | As-built + target Mermaid diagrams, citations, inferred items | Done (diagrams hand-written, not tool-rendered) | `01-architecture.md` |
| 1b | One executable architecture test | Done | `backend/tests/InvoiceApp.Tests/DomainArchitectureTests.cs`; suite 8 passed; mutation check fails as intended |
| 2 | Exactly-once decision record | Draft done, **author must review and own** | `02-exactly-once-decision-record.md` |
| 3 | Autonomy policy | Draft done, **author must review and own** | `03-autonomy-policy.md` |
| 4 | Eval: 2 added cases, 3 baseline runs, 1 variable, rerun, rates, confidence | Done | `04-eval-report.md`, `ops/evals/results.csv`, `ops/evals/runs/`, `scripts/eval_report.py` |
| 5a | Lethal-trifecta audit + decision | Done (README has no agent section; audited what exists) | `05-risk-audit.md` |
| 5b | Measurement plan + two numbers | Done, numbers are proxies from invented planned-pipeline data | `06-measurement-plan.md`, `scripts/ci_metrics.py` |
| 6 | AI augmentation log | Done | `07-ai-augmentation-log.md` |
| 7 | 8-10 min demo video, uploaded and linked | **BLOCKED** (cannot record/upload); script ready | `08-demo-script.md`; video link: _add here_ |

Known limitations: Mermaid not validated by a tool; evals scored by the same model family, not blind, small
sample; no real CI history exists for this repo yet; `.mcp.json` not pinned (recommendation only).

Reproduce: `export PATH=$HOME/.dotnet:$PATH; dotnet test backend/InvoiceApp.sln`,
`python3 scripts/eval_report.py`, `python3 scripts/ci_metrics.py`.
