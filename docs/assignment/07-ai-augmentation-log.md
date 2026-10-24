# AI augmentation log

Honest record of where AI was used. The AI was GitHub Copilot CLI (Claude Sonnet 5.5) working in the
submission repo under the user's instruction. The user did not write these deliverables; they must review and
own them (especially the decision record and autonomy policy, which the assignment wants in the author's voice).

| Area | What the AI did | What I would check / limits |
|---|---|---|
| Orientation | Read the assignment PDF, `ops/README.md`, source, CI, evals, git history; reported mismatches (no agent section in the README; eval diffs reference symbols absent from the tree) | Spot-check the mismatches listed in `docs/assignment/05-risk-audit.md` and `01-architecture.md` section 5 |
| Setup | Imported starter history into AIinSDLC (`git pull` from the local starter, 6 commits kept), installed .NET 8 SDK to `~/.dotnet`, ran baseline build/tests (7 passed) | No push to the starter repo; origin of the starter was never touched |
| 1. Architecture | Hand-wrote Mermaid diagrams from reading code and listed citations and inferences. **No Mermaid MCP was available**; diagrams were not rendered or validated by a tool | Render them (GitHub renders Mermaid) and verify against code |
| 1. Architecture test | Wrote `DomainArchitectureTests.cs`; ran it (8 pass); proved it can fail via a temporary `HttpClient` mutant, then removed the mutant | Reference-based check only; documented limit |
| 2. Decision record | A `general-purpose` sub-agent argued the options and answered three stress tests; the assistant then judged its output and drafted the record | The "wrong or useless" section is the assistant's critique; the author must form their own view. Cost numbers are estimates |
| 3. Autonomy policy | Drafted from the incident packs | Author owns thresholds and approver choice |
| 4. Evals | Wrote 2 cases (11 real, from INC-2041; 12 clean, from a real commit), pre-registered the key (sha256 in the report), ran 72 reviewer sessions (36 baseline v1, 36 v2) as fresh `explore` sub-agents, scored them, computed Wilson intervals with `scripts/eval_report.py` | Same model family reviews and scores; not blind; model ID not exposed; ceiling effect; low confidence (see report) |
| 5. Risk audit | Audited `.mcp.json`, `AGENTS.md`, incident workflow; did not modify `.mcp.json` | Version pin left for the author |
| 5. Metrics | `scripts/ci_metrics.py` on `ops/pipeline/run-timings.csv` | Data is for the invented planned pipeline; proxies only |
| Hand-in | Drafted demo script and checklist | **Video not recorded or uploaded** (AI cannot do this) |

Failures and corrections during the work (kept on purpose):
- The test first failed to compile (missing `using Xunit;`); fixed.
- An early attempt to write the architecture doc failed because `docs/assignment/` did not exist; created the folder and rewrote.
- In baseline run 3 a reviewer raised a clock-adjustment flakiness claim on a clean case; scored as a false alarm, not hidden.
- v2 prompt did not improve case-09 detection (it did worse); reported as is, not retuned afterwards.

Not used / not available: Mermaid MCP, `gh` CLI, any model-selection control for sub-agents, any production or
external service. No secrets were used; the only credentials in the repo are the documented demo accounts.
