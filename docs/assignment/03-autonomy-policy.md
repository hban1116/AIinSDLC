# Deliverable 3 - Autonomy policy: first-response incident summaries

> DRAFT for the author to review and own. One workflow only.

**Workflow:** when an alert fires, an agent reads the read-only evidence (alert, publisher/worker logs, queue
status, recent changes - the shape of `ops/incidents/INC-2047`) and produces a first-response summary: what is
observed, what is not known, two or three mitigation options with cost and undo. Chosen because it matches the
evidence packs, its output is advisory text, and a wrong answer is caught by the human on call.

## Levels

| Level | What the agent may do | Production writes |
|---|---|---|
| L0 | Nothing; humans only | none |
| L1 (**day one**) | Read exported evidence, draft a summary and options. A human reads the raw evidence too and does not rely on the summary alone | none |
| L2 | Same, plus read-only queries on a defined list (logs, queue depth), summary posted to the incident channel as "draft" | none |
| L3 | Propose a specific mitigation in a runbook-defined format for approval with one click | only after a named human approves |
| Never | Execute a mitigation on its own, touch payments or customer data, rollback, restart | - |

## Controls (all levels)

- Read-only credentials; no write-capable tool is configured (see `05-risk-audit.md`, setup C).
- Log text is treated as data, never as instructions. Evidence is exported, not streamed live.
- Every claim in the summary cites a file and line; unknowns are listed explicitly. Uncited claims are not used.
- Output is labelled DRAFT and carries a timestamp and the evidence version it saw.
- Every use is logged (input files, output, who acted on it), to make promotion evidence possible.
- Any production change needs a named approver (incident commander out of hours); the agent never is that approver.
- Kill switch: any engineer can disable the workflow; turning it off must not block incident response.

## Day-one level and why

**L1.** Two of six engineers are new and cannot yet tell a plausible-but-wrong summary from a sound one, and they
are the people most likely to trust it. At L1 the summary is a second opinion alongside the raw evidence, an
experienced engineer reviews the first incidents, and the new engineers pair with them.

## Evidence needed to move up

- L1 to L2: at least 10 real or replayed incidents in which the summary's facts were checked, with no
  fabricated facts and no missed key signal that the humans later found important; every missed signal reviewed.
  Replaying INC-2041/2047 counts only if the agent has not seen the answers.
- L2 to L3: 20+ incidents at L2 with the proposed mitigations judged correct or acceptable in at least 90% by
  two reviewers, no case where the agent proposed an irreversible action without flagging it, and a runbook for
  each mitigation it may propose. With samples this small the rate is a guide, not a proof; keep human approval.
- Any fabricated fact or unsafe suggestion drops the workflow one level until reviewed.

## Approver and review

The head of engineering (or delegate) approves any level change in writing, after reading the usage log. Review
monthly for the first quarter, then quarterly. The incident commander on call may drop the level immediately.
