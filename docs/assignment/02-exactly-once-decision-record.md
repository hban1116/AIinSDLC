# Deliverable 2 - Decision record: exactly-once PayEx submission after approval


## Context

When an approver approves an invoice, a payment must reach the external provider PayEx exactly once. Today
`ApprovalService.Approve` only flips the status in memory (`docs/assignment/01-architecture.md`); there is no
database, queue or PayEx client. The plan assumes Azure SQL and an already-provisioned Azure Service Bus.
Constraint that makes this hard: PayEx calls can time out at 30 s without telling us whether the payment happened,
and INC-2041 shows what a naive synchronous call does (per-call `HttpClient`, socket exhaustion, approve committed
but payment failed). "Exactly once" is not achievable end to end; the realistic target is **at-least-once delivery
with idempotent effect**, plus detection of what slips through.

## Options

| | A. Synchronous call in the request | B. Transactional outbox + worker | C. Reconciliation only (detective) |
|---|---|---|---|
| How | Approve then call PayEx inline, retry on failure | In one SQL transaction write status + audit + outbox row; a background worker claims rows and calls PayEx with a deterministic idempotency key | Submit loosely, compare our records with PayEx daily and fix differences |
| Duplicate risk | High on timeout/retry; dual-write gap | Low if PayEx honours the key; "unknown" state on timeout instead of a blind resend | Duplicates happen and are found later |
| Lost-payment risk | Approved but never sent (INC-2041 shape) | Low: the row is durable | Found at reconciliation, up to a day later |
| Effort (estimate) | 8-14 engineer-days | 22-36 engineer-days | 10-18 plus heavy ops hours |
| Month-end behaviour | Latency and failures hit approvers directly | Backlog drains at worker pace; approvers unaffected | Same as A until reconciled |

## Decision

Choose **B**, with **C as a detective control** on top, and keep Service Bus out of the payment path for now. The
outbox is polled by a SQL-backed `BackgroundService` (lease-claim rows, one deterministic idempotency key per invoice
approval). On timeout the row goes to an `unknown` state that is resolved by lookup or by a human, never by blindly
resending. Choose A only as a short stop-gap if we ship before January and accept the duplicate risk in writing.

The **pivotal unknown** is whether PayEx honours idempotency keys or lets us look a payment up by our reference.
This decision is conditional on that answer and must be confirmed with PayEx before work starts.

## Stress tests

1. **Preference shift: the team prefers C.** The recommendation does not change on preference alone, because C
   accepts duplicates and a day of lost-payment exposure for a payments flow. What would move it: PayEx offering
   idempotency or lookup by reference (makes a lightweight B cheap), a relaxed business requirement, measured
   duplicate rates showing it is rare, or a credible estimate that B cannot land by January. Compromise: write the
   outbox row in the Approve transaction now, run a single-instance poller, add nightly reconciliation.
2. **3 a.m. on month-end: PayEx is timing out.** At an assumed 80 approvals/minute, 40 minutes of outage leaves about
   3,200 rows queued. With B nothing is lost; the worker backs off and drains afterwards. Operators need a pause
   switch, a runbook, an alert on queue age and `unknown` count, and a rule never to hand-edit state. With A,
   approvers see errors and retry, which creates duplicates. (Assumed rate; replace with real month-end volumes.)
3. **Build/run cost.** B costs roughly 2x A to build and adds a worker, a table and alerts to run; C is cheaper to
   build but costs ongoing human reconciliation time. The PayEx idempotency answer swings B by roughly 5-8 days.
   All numbers are the assistant's estimates and should be replaced by the team's own.

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
