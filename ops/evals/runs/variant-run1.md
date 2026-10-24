# Changed-variable run 1 (prompt v2) - raw reviewer outputs

Only the review prompt changed (v1 -> v2, see `docs/assignment/04-eval-report.md`); model, case files and session setup are the same.
Fresh `explore` sub-agent session per case. Verbatim.

## case-01
- **File:** `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`
- **Line:** 49 (`foreach (var id in request.Ids)`)
- **Defect:** `Ids` is nullable, but the method iterates it without checking for `null`. Sending `{}`, `{"ids": null}`, or a `null` request body causes a `NullReferenceException` and an HTTP 500 response instead of a validation error.
- **Confidence:** High

## case-02
- **`backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:27,31`** — `customer` and `status` are interpolated directly into SQL. A request such as `GET /search?customer=' OR 1=1 --` changes the query predicate and can return all invoices; a malicious `status` can similarly alter the query or execute injected SQL, depending on the database. **Confidence: High.**

## case-03
- **File:** `backend/src/InvoiceApp.Domain/DiscountCalculator.cs`  
  **Line:** 15  
  **Defect:** Using `MidpointRounding.ToZero` for the final result truncates rather than rounds to the nearest cent. For example, `Apply(100m, 12.346m)` returns `87.66m`, although the unrounded result is `87.654m` and should round to `87.65m` (as the previous implementation did).  
  **Confidence:** High

## case-04
No defects found.

## case-05
Finding:
- **File:** `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`
- **Line:** Added `Delete(string id)` method
- **Defect:** The endpoint has no authorization attribute, unlike `Update`, so any unauthenticated or unauthorized caller who can reach the route can delete an invoice.
- **Trigger/consequence:** A caller sends `DELETE /{id}` for an invoice ID; `_repository.Delete(id)` executes and the API returns `204 No Content`, allowing unauthorized data deletion.
- **Confidence:** High

## case-06
No defects found.

## case-07
- **File:** `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`  
  **Line:** 34  
  **Defect:** Every successful approval logs the complete invoice payload and current session/user object. An approver approving an invoice causes potentially sensitive financial and identity/session data to be written to application logs, exposing it to anyone with log access.  
  **Confidence:** High

## case-08
- **File:** `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs`, lines 9, 18–26  
  **Defect:** Replacing `ConcurrentDictionary` with `Dictionary` makes repository operations unsafe under concurrent requests. For example, simultaneous `Add` or `Update` calls can race during dictionary mutation, causing exceptions or lost/inconsistent entries.  
  **Confidence:** High.

## case-09
- **README.md:22–24** — The instruction to “reset the sample data” by signing out and signing in again is unsupported and contradicts the preceding statement that data is recreated only when the process starts. If a user signs out and back in during the same process, their entered data remains instead of resetting, causing the documented reset procedure to fail. **Confidence: High**

## case-10
- **File:** `/mnt/c/Users/harshitbansal/Downloads/AIinSDLC/AIinSDLC/ops/evals/cases/case-10.diff`, lines 35–37  
  **Defect:** The catch-all handler converts every unexpected exception into HTTP 200 with `{"status":"completed"}`. Any database, authorization, or programming failure during `action()` therefore appears to the client as a successful operation, while the actual error is hidden.  
  **Confidence:** High

## case-11
- `src/InvoiceApp.Api/Clients/PayExClient.cs:15-25` — A new `HttpClient` is created for every submission and never disposed. Repeated approvals can leave many handlers/sockets undisposed, eventually causing resource exhaustion and failed payment requests. **Confidence: high**

- `src/InvoiceApp.Api/Controllers/ApprovalsController.cs:38-39` — The invoice is approved before PayEx submission. If PayEx returns an error or times out, the endpoint returns an error while the invoice remains approved, leaving local approval and payment state inconsistent. **Confidence: high**

- `src/InvoiceApp.Api/Contracts/DecisionResponse.cs:5-6` — Renaming response properties to `ApprovedBy` and `ApprovedAt` also affects rejected-invoice responses. A rejection now serializes approval-specific field names, changing the API contract and mislabeling rejection metadata. **Confidence: high**

## case-12
No defects found.
