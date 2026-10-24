# Baseline run 1 (prompt v1) - raw reviewer outputs

Each case was reviewed by a separate, fresh `explore` sub-agent session (Copilot CLI, default model; the model
identifier is not exposed to the harness, see report). Outputs are verbatim.

## case-01
- **File:** `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`  
  **Line:** `foreach (var id in request.Ids)`  
  **Issue:** `Ids` is nullable, so a request with a missing or `null` `ids` property causes a `NullReferenceException` and returns a server error instead of a validation response.  
  **Confidence:** High.

## case-02
- **File:** `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`  
  **Line:** 27 (also line 31)  
  **Issue:** User-controlled `customer` and `status` values are interpolated directly into SQL, allowing SQL injection through the search query.  
  **Confidence:** High.

## case-03
- `/mnt/c/Users/harshitbansal/Downloads/AIinSDLC/AIinSDLC/ops/evals/cases/case-03.diff:16-17` — Replacing `MidpointRounding.AwayFromZero` with `ToZero` truncates fractional cents rather than rounding them, producing incorrect invoice totals (e.g., a calculated discount of 1.239 becomes 1.23 instead of 1.24). **Confidence: High**

## case-04
No defects found.

## case-05
- **`backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:44-50`** — `Delete` lacks the `[RequireRole("Admin")]` authorization attribute present on `Update`, so users without the required admin role may delete invoices. **Confidence: High**

## case-06
No defects found in the provided diff.

## case-07
- `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs:33-35` — Logs the complete invoice payload and current user object, which may expose sensitive financial or personal data in application logs. **Confidence: High**

## case-08
- **File:** `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs`  
  **Line:** 9  
  **What goes wrong:** Replacing `ConcurrentDictionary` with `Dictionary` makes repository operations unsafe under concurrent requests. Concurrent reads/writes or simultaneous `Add` calls can cause data corruption, exceptions, or bypass the duplicate-ID check.  
  **Confidence:** High

## case-09
No defects found in the provided diff.

## case-10
- **File:** `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs`  
  **Line:** 35–38  
  **Issue:** The broad `catch (Exception)` converts every unexpected failure into HTTP 200 with `{ status = "completed" }`. This hides server errors, falsely reports failed operations as successful, and prevents normal exception handling/monitoring.  
  **Confidence:** High

## case-11
- `src/InvoiceApp.Api/Clients/PayExClient.cs:17-22` — A new `HttpClient` is created for every submission and never disposed. Repeated approvals can exhaust sockets/resources and cause connection instability. **Confidence: high.**

- `src/InvoiceApp.Api/Controllers/ApprovalsController.cs:38-40` — The invoice is approved before the PayEx submission. If PayEx fails, the request errors while the invoice remains approved; retries may submit the same payment multiple times because no idempotency or compensation is shown. **Confidence: high.**

- `src/InvoiceApp.Api/Contracts/DecisionResponse.cs:5-6` — Renaming response fields from `DecidedBy`/`DecidedAt` to `ApprovedBy`/`ApprovedAt` changes the API contract for all consumers, including rejection responses that still use the same response type. **Confidence: medium.**

## case-12
No defects found.
