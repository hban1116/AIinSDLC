# AI augmentation log

Honest record of where AI was used. The AI was GitHub Copilot CLI (Claude Sonnet 5.5) working in the
submission repo under the user's instruction. The user did not write these deliverables; they must review and
own them (especially the decision record and autonomy policy, which the assignment wants in the author's voice).

| Area | What the AI did | What I would check / limits |
|---|---|---|
| Orientation | Read the assignment PDF (not in the repo, so this claim cannot be verified from the repo), `ops/README.md`, source, CI, evals, git history; reported mismatches (no agent section in the README; eval diffs reference symbols absent from the tree) | Spot-check the mismatches listed in `docs/assignment/05-risk-audit.md` and `01-architecture.md` section 5 |
| Setup | Imported starter history into AIinSDLC (`git pull` from the local starter, 6 commits kept), installed .NET 8 SDK to `~/.dotnet`, ran baseline build/tests (7 passed) | No push to the starter repo; origin of the starter was never touched |
| 1. Architecture | Hand-wrote Mermaid diagrams from reading code and listed citations and inferences. Initially no Mermaid MCP was available in that session, so the diagrams were not tool-validated. In the 2026-10-24 audit session the Mermaid Chart MCP tool `validate_and_render_mermaid_diagram` was called once per diagram (3 calls, all rendered without error); see `01-architecture.md` section 2a | MCP success means the syntax renders, not that the diagrams match the code; citations were re-read against source |
| 1. Architecture test | Wrote `DomainArchitectureTests.cs`; ran it (8 pass); proved it can fail via a temporary `HttpClient` mutant, then removed the mutant | Reference-based check only; documented limit |
| 2. Decision record | A `general-purpose` sub-agent argued the options and answered three stress tests; the assistant then judged its output and drafted the record | The "wrong or useless" section is the assistant's critique; the author must form their own view. Cost numbers are estimates |
| 3. Autonomy policy | Drafted from the incident packs | Author owns thresholds and approver choice |
| 4. Evals | Wrote 2 cases (11 real, from INC-2041; 12 clean, from a real commit), pre-registered the key (sha256 in the report), ran 72 reviewer sessions (36 baseline v1, 36 v2) as fresh `explore` sub-agents, scored them, computed Wilson intervals with `scripts/eval_report.py` | Same model family reviews and scores; not blind; model ID not exposed; ceiling effect; low confidence (see report) |
| 5. Risk audit | Audited `.mcp.json`, `AGENTS.md`, incident workflow; did not modify `.mcp.json` | Version pin left for the author |
| 6. Metrics | `scripts/ci_metrics.py` on `ops/pipeline/run-timings.csv` | Data is for the invented planned pipeline; proxies only |
| Hand-in | Drafted demo script and checklist | **Video not recorded or uploaded** (AI cannot do this) |

Failures and corrections during the work (kept on purpose):
- The test first failed to compile (missing `using Xunit;`); fixed.
- An early attempt to write the architecture doc failed because `docs/assignment/` did not exist; created the folder and rewrote.
- In baseline run 3 a reviewer raised a clock-adjustment flakiness claim on a clean case; scored as a false alarm, not hidden.
- v2 prompt did not improve case-09 detection (it did worse); reported as is, not retuned afterwards.

Not used / not available: any model-selection control for sub-agents, any production or
external service. No secrets were used; the only credentials in the repo are the documented demo accounts.

2026-10-24 audit session (Copilot CLI, Claude Sonnet 5.5) - what was actually done:
- Re-checked the deliverables; made 3 Mermaid MCP calls (flowchart, sequence, flowchart; `clientName: copilot-cli`,
  `useUrlShortener: false`), all succeeded on the first attempt. No credential was written anywhere.
- Corrections: the ADR options did not match the three required approaches and implied the outbox alone gives
  exactly-once (fixed); the autonomy policy named an approver nobody established (withdrawn, flagged as a gap); the
  measurement plan wrongly said `gh` was unavailable and now records zero real PRs/runs; the eval report gained an
  explanation of how `results.csv` is generated; the `gh` claims above were verified by running the commands.
- Ran: `scripts/eval_report.py`, `scripts/ci_metrics.py`, `dotnet test`; results are in the final report to the user.
- Human verification still needed: the author must read the ADR/policy, spot-check evals, and record/upload the demo.
- Adversarial challenges in the ADR were written by the assistant itself, not independent sessions.
