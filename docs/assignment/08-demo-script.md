# Demo script (8-10 minutes)

The video itself is **not recorded or uploaded** (the AI cannot record). Record this yourself, upload it, and put
the link in `docs/assignment/README.md`. Timings add to ~9:30.

| Time | Show | Say |
|---|---|---|
| 0:00-0:45 | Repo, `AGENTS.md`, `ops/README.md` | The app, the planned production, and that I only trust code, not the ops docs |
| 0:45-2:15 | `01-architecture.md` diagrams | As-built vs target; point at one citation (`Program.cs:14`, `ApprovalService.Approve`); the corrections table; Mermaid was hand-written (no MCP) |
| 2:15-3:15 | Run `dotnet test backend/InvoiceApp.sln` | 8 pass; open `DomainArchitectureTests.cs`; show the mutant failure from the doc |
| 3:15-4:45 | `02-exactly-once-decision-record.md` | Options, the choice (B + C), the pivotal PayEx unknown, and **where the agent was wrong**. Say what you changed from the draft |
| 4:45-5:45 | `03-autonomy-policy.md` | Day-one L1 and why, promotion evidence, approver |
| 5:45-7:45 | `04-eval-report.md`, `ops/evals/results.csv`, run `python3 scripts/eval_report.py` | Pre-registered key and hash, 3 baseline runs, one variable, results, "not demonstrably better", low confidence, case-09 sensitivity |
| 7:45-8:45 | `05-risk-audit.md` | Three legs per setup, the README discrepancy, decisions and revisit triggers |
| 8:45-9:30 | `06-measurement-plan.md` and `07-ai-augmentation-log.md` | The two proxy numbers and why they are proxies; what the AI did and did not do |

Before recording: reread each document and change anything you disagree with; the decision record and policy
should be your own judgement.
