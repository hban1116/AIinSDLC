# Baseline run 3 (prompt v1) - raw reviewer outputs

Fresh `explore` sub-agent session per case, default model. Verbatim (long absolute paths not present in these outputs).

## case-01
- **File:** `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`  
  **Line:** `foreach (var id in request.Ids)`  
  **Issue:** `Ids` is nullable, so a request with a missing or `null` `ids` value causes a `NullReferenceException`, likely returning a 500 response instead of a validation error.  
  **Confidence:** High.

## case-02
- **File:** `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`
- **Line:** 28
- **Issue:** User-controlled `customer` and `status` values are interpolated directly into SQL, allowing SQL injection. An attacker can alter the query or execute unintended database operations.
- **Confidence:** High

## case-03
- **File:** `backend/src/InvoiceApp.Domain/DiscountCalculator.cs`  
  **Line:** 16–17  
  **What goes wrong:** The calculation now rounds both the discount and final amount toward zero, truncating fractional cents instead of rounding away from zero as before. This produces incorrect invoice totals for values with fractions of a cent (and can systematically under/overcharge).  
  **Confidence:** High

## case-04
No defects found.

## case-05
- `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:44` — `Delete` lacks the `[RequireRole("Admin")]` authorization attribute present on `Update`, allowing users without the Admin role to delete invoices. **Confidence: High**

## case-06
- **File:** `backend/tests/InvoiceApp.Tests/ApprovalServiceTests.cs`  
  **Line:** 83  
  **Issue:** The assertion compares `DecidedAt` against two live `DateTime.UtcNow` calls. A system clock adjustment during the test could make a valid result fall outside the range, causing intermittent failures.  
  **Confidence:** Medium

## case-07
- `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs:34-36` — Logs the complete invoice payload and current user/session object, potentially exposing sensitive financial and identity data in application logs. **Confidence: High**

## case-08
- **File:** `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs`  
  **Line:** 9  
  **Defect:** Replacing `ConcurrentDictionary` with `Dictionary` makes `GetById`, `Add`, and `Update` unsafe under concurrent requests. Concurrent reads/writes can race, corrupt dictionary state, or throw exceptions.  
  **Confidence:** High

- **File:** `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs`  
  **Lines:** 19–25  
  **Defect:** `ContainsKey` followed by assignment is not atomic. Concurrent `Add` calls for the same ID can both pass the check, with one silently overwriting the other instead of throwing the duplicate exception.  
  **Confidence:** High

## case-09
- **README.md, line 24** — The claim that signing out and signing in again resets sample data is likely incorrect: authentication state changes generally do not recreate or clear an in-memory data store. **Confidence: Medium**

## case-10
- `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs:33` — The new catch-all handler converts every unexpected exception into HTTP 200 with `status = "completed"`, hiding server failures from clients and monitoring and falsely indicating successful operations. **Confidence: High**

## case-11
- `src/InvoiceApp.Api/Clients/PayExClient.cs:15-18` — A new `HttpClient` is allocated for every submission and never disposed. This can exhaust sockets and cause connection failures under load. **Confidence: High**

- `src/InvoiceApp.Api/Controllers/ApprovalsController.cs:39-40` — The invoice is approved before the PayEx submission. If PayEx fails, the request returns an error while the invoice remains approved, and retries may submit it again, potentially creating duplicate payments. **Confidence: High**

- `src/InvoiceApp.Api/Contracts/DecisionResponse.cs:6-7` — Renaming response properties from `DecidedBy`/`DecidedAt` to `ApprovedBy`/`ApprovedAt` is a breaking API contract change for existing clients, including rejection responses that still use this type. **Confidence: High**

## case-12
No defects found.
