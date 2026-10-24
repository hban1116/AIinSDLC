# Deliverable 2 - Decision record: exactly-once PayEx submission after approval


## Context

When an approver approves an invoice, a payment must reach the external provider PayEx exactly once. Today
`ApprovalService.Approve` only flips the status in memory (`docs/assignment/01-architecture.md`); there is no
database, queue or PayEx client. The plan assumes Azure SQL and an already-provisioned Azure Service Bus.
Constraint that makes this hard: PayEx calls can time out at 30 s without telling us whether the payment happened,
and INC-2041 shows what a naive synchronous call does (per-call `HttpClient`, socket exhaustion, approve committed
but payment failed). "Exactly once" is not achievable end to end; the realistic target is **at-least-once delivery
with idempotent effect**, plus detection of what slips through.

## What "exactly once" can and cannot mean here

No mechanism on our side can make a call to an external system happen exactly once. If we send a request and the
connection times out, we cannot tell "PayEx never received it" from "PayEx processed it and the reply was lost".
So the choices are: resend (possible duplicate) or do not resend (possible lost payment). What is achievable is
**at-least-once delivery combined with an idempotent effect**, and that only holds if PayEx cooperates (honours an
idempotency key, or lets us look a payment up by our own reference). If PayEx offers neither, no option below
gives exactly-once effects; we are then limited to detecting duplicates and lost payments after the fact.

Consequences for the options: a transactional outbox makes *our own* side reliable (status change and "payment
to send" commit together, so approval is never recorded without a pending send). It does **not** by itself
guarantee exactly-once at PayEx: the worker can still crash after PayEx accepted the call but before we record
the result, and will then resend. Only an idempotency key / reference lookup honoured by PayEx turns that resend
into a no-op.

## Options

| | A. Idempotency key + deduplication | B. Transactional outbox + worker | C. Optimistic submission + nightly reconciliation |
|---|---|---|---|
| How | The approve request (or a retry wrapper) calls PayEx with a deterministic key per approval (for example invoice id + approval id); we keep a dedupe record so repeated requests for the same approval return the first result | In one SQL transaction write status + audit + outbox row; a background worker claims rows and calls PayEx with the same deterministic key; on timeout the row goes to `unknown` | Submit right after approval without durable intent tracking, retry a little, and compare our approvals with PayEx's records each night; fix differences by hand or script |
| Duplicate risk | Low **only if PayEx enforces the key**; otherwise our dedupe record covers repeats of *our* request but not a lost reply | Same dependency on PayEx. Without the key, a worker crash between PayEx success and our write causes a resend | Duplicates happen and are found up to a day later |
| Lost-payment risk | Approve committed but call never made if the process dies between the two steps (dual write, INC-2041 shape) unless combined with something durable | Low: the row is durable and retried | Found at reconciliation, up to a day later |
| What it does not solve | The dual-write gap between the database commit and the external call | Exactly-once at PayEx without PayEx idempotency or lookup; also the `unknown` state needs a human or a lookup | Anything in real time; money may move twice before anyone sees it |
| Effort (estimate, not measured) | 8-14 engineer-days | 22-36 engineer-days | 10-18 plus ongoing ops hours |
| Month-end behaviour | Latency and failures hit approvers directly if the call is inline | Backlog drains at worker pace; approvers unaffected | Same as an unsafe inline call until reconciled |

## Decision

Choose **B**, using the **idempotency key from A on every send** and **C as a detective control** on top, and keep
Service Bus out of the payment path for now. A is not an alternative to B here but the part of B that creates the
exactly-once *effect*; B alone only creates reliable delivery. The outbox is polled by a SQL-backed
`BackgroundService` (lease-claim rows, one deterministic idempotency key per invoice approval). On timeout the row
goes to an `unknown` state that is resolved by lookup or by a human, never by blindly resending. A bare inline call
(no outbox) is acceptable only as a short stop-gap if we ship before January and accept the duplicate risk in
writing.

The **pivotal unknown** is whether PayEx honours idempotency keys or lets us look a payment up by our reference.
This decision is conditional on that answer and must be confirmed with PayEx before work starts. If PayEx offers
neither, C becomes the primary control and the business must accept that duplicates are possible and detected late.

## Stress tests

1. **Preference shift: the team prefers C.** The recommendation does not change on preference alone, because C
   accepts duplicates and a day of lost-payment exposure for a payments flow. What would move it: PayEx offering
   idempotency or lookup by reference (makes a lightweight B cheap), a relaxed business requirement, measured
   duplicate rates showing it is rare, or a credible estimate that B cannot land by January. Compromise: write the
   outbox row in the Approve transaction now, run a single-instance poller, add nightly reconciliation.
2. **3 a.m. on month-end: PayEx is timing out.** At an assumed 80 approvals/minute, 40 minutes of outage leaves about
   3,200 rows queued. With B nothing is lost; the worker backs off and drains afterwards. Operators need a pause
   switch, a runbook, an alert on queue age and `unknown` count, and a rule never to hand-edit state. With a bare inline call
   (no outbox), approvers see errors and retry, which creates duplicates unless PayEx enforces the key. (Assumed rate; replace with real month-end volumes.)
3. **Build/run cost.** B costs roughly 2x A to build and adds a worker, a table and alerts to run; C is cheaper to
   build but costs ongoing human reconciliation time. The PayEx idempotency answer swings B by roughly 5-8 days.
   All numbers are the assistant's estimates and should be replaced by the team's own.

## Adversarial challenges to this decision

Raised during the 2026-10-24 audit by the Copilot CLI assistant, answering its own earlier draft. They were not
run as separate sessions and no independent transcript exists; the author should rerun them with their own prompts.

1. *"The outbox gives you exactly-once."* No. The worker can crash after PayEx accepts and before the result is
   stored, then resend. Exactly-once effect needs PayEx-side idempotency or lookup (see the limits section).
2. *"The idempotency key is deterministic, so duplicates are impossible."* Only if PayEx retains keys long enough
   (a retry after the key expires is a new payment) and treats a changed amount under the same key safely. The
   retention window is unknown and must be confirmed.
3. *"Mark `unknown` and have a human decide: that does not scale on month-end."* At the assumed 80 approvals per
   minute even a 0.5% timeout rate (an assumed figure) is hundreds of manual cases. Lookup by reference must be
   automated, which again depends on PayEx.
4. *"Two workers or two app instances claim the same row."* A lease with a conditional update (claim only if
   unclaimed or expired) is required; an expired lease can still cause a concurrent send, which is again only
   safe because of the key.
5. *"Approve is check-then-act today, so two approvals can both create outbox rows."* Correct: a unique constraint
   on the idempotency key / invoice id and an atomic status transition in SQL are needed; the in-memory
   repository gives no such guarantee (`01-architecture.md`, inferred item 4).
6. *"Nightly reconciliation finds problems after money moved."* True: it is detective, not preventive, and cannot
   undo a payment; it limits the damage window to about a day.
7. *"You chose B because it is the most engineering."* Fair. B costs about twice A by the assistant's estimate
   (not measured); it is justified only because payments are hard to undo. If duplicate rates prove negligible and
   PayEx supports lookup, a lighter option should be reconsidered.

## What would make us revisit

- PayEx has no idempotency or lookup support (B's core guarantee weakens; reconciliation becomes primary).
- Measured month-end volume far below or above the assumed 80/minute.
- Duplicate or lost payments observed in reconciliation despite B.
- The team cannot staff the worker's on-call, or Service Bus becomes mandatory for another consumer.

## Where the agent was wrong or useless

The agent here was a sub-agent given the scenario text and asked to argue the options and answer the three stress
tests. Judged by me afterwards:

- **Useless on the central question.** The recommendation is conditional on whether PayEx supports idempotency,
  which the agent could not know and which is not in the repo. Everything else rests on that.
- **Internally inconsistent estimates.** In the "team prefers C" answer a minimal B was "a week or two"; in the
  cost answer B was 22-36 engineer-days (4-7 weeks). Both cannot hold; I treat the larger figure as safer.
- **Overstated risk.** "Up to ~3,200 duplicate payments" is a worst case; only calls that timed out *and* actually
  succeeded would duplicate. The 0.5% / 200-case failure figure was its own assumption, not data.
- **No grounding in the code.** It never mentioned that `ApprovalService.Approve` is check-then-act on a shared
  object (two concurrent approvals can both pass `EnsurePending`), that Admin can approve an invoice they created,
  or that nothing in the code enforces a second approver. Those matter more for payments than the queue choice.
- **Dismissed Service Bus quickly.** It is already provisioned; I agreed with keeping it out of the payment path,
  but that call should be made by the team with the cost of running both in view, not on the agent's say-so.
- **Unsourced numbers.** All effort and volume numbers are estimates with no basis in this repository.
- **Wrong option framing in the first draft (found in the 2026-10-24 audit).** The first draft's option A was a
  bare inline call with retries, not "idempotency key + deduplication", and its option C was "reconciliation
  only". That did not compare the three approaches the assignment names, and it let the outbox read as if it
  alone solved duplicates. Both are corrected above.
