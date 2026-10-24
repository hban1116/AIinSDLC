# Review-eval ground truth (pre-registered before any review run)

Source: the starter repo does NOT record which cases are defective (ops/evals/README.md says so).
This key is the submitter's own reading of each diff, written before any review was run.
Cases 01-10 are the original fixed cases; 11-12 are added.

Scoring rule: a defective case is CAUGHT only if the review names the defect described under "Must name".
Naming only another problem = MISSED (even if the other problem is real). A clean case is a FALSE ALARM only
if the review asserts a defect (a bug/vulnerability/regression); style or naming suggestions are not false alarms.
Saying "no defect found" on a clean case = CORRECT. On a defective case with nothing relevant = MISSED.

| Case | Truth | Must name |
|---|---|---|
| 01 | defect | bulk-approve: `request.Ids` is nullable and dereferenced (NullReferenceException on missing/null body list) OR the loop is not atomic/not failure-tolerant: an exception mid-loop leaves earlier invoices approved while the caller gets an error |
| 02 | defect | SQL injection: `customer` and `status` concatenated into the SQL string |
| 03 | defect | Rounding behaviour change in money maths: truncation (MidpointRounding.ToZero) and double rounding of the discount, changing amounts vs the previous AwayFromZero rounding |
| 04 | clean | pure rename `_repository` -> `_invoices`; no behaviour change |
| 05 | defect | new DELETE endpoint has no `[RequireRole("Admin")]`, so any signed-in user (the neighbouring Update is Admin-only) can delete invoices |
| 06 | clean | three added unit tests, all consistent with the service behaviour |
| 07 | defect | logs entire invoice object and session object (`{@Invoice}`, `{@Session}`): sensitive data / session details in logs |
| 08 | defect | `ConcurrentDictionary` replaced by plain `Dictionary` in a shared repository: not thread-safe (races, check-then-add) |
| 09 | defect | README says signing out and in resets the sample data. False: the repository is a singleton and logout only removes the session token (`SessionStore.Remove`). (Uncertain key: if the case designer meant 09 as clean, see sensitivity analysis in the report.) |
| 10 | defect | catch-all `catch (Exception)` returns 200 "completed": unexpected failures are reported as success |
| 11 | defect | `PayExClient.SubmitAsync` creates a new `HttpClient` per call (socket exhaustion / lost connection pooling; removed `AddHttpClient` registration). Corroborated by INC-2041 logs: SocketException 10048 |
| 12 | clean | real commit 3834913: .gitignore entries, AGENTS.md doc lines, coverlet.collector package reference, no defect |
