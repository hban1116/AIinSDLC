# Baseline run 2 (prompt v1) - raw reviewer outputs

Fresh `explore` sub-agent session per case, default model. Verbatim, except that the long absolute path prefix in case-08 is abbreviated to `...`.

## case-01
- `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs:49` — `request.Ids` is nullable, but it is enumerated without a null check. A request with omitted or null `Ids` causes a `NullReferenceException` instead of a validation response. **Confidence: High**

## case-02
- **File:** `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`  
  **Line:** 28  
  **Issue:** User-controlled `customer` and `status` values are interpolated directly into SQL, allowing SQL injection. An attacker could alter the query or access/modify unintended data.  
  **Confidence:** High

## case-03
- **File:** `backend/src/InvoiceApp.Domain/DiscountCalculator.cs`  
  **Line:** 16–17  
  **Issue:** The calculation now rounds both the discount and final amount using `MidpointRounding.ToZero`, truncating fractional cents instead of applying the previous `AwayFromZero` monetary rounding. For example, an amount producing `87.665` is returned as `87.66` rather than `87.67`, causing incorrect totals.  
  **Confidence:** High

## case-04
No defects found.

## case-05
- **File:** `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`  
  **Line:** 44  
  **Issue:** The new delete endpoint lacks the `[RequireRole("Admin")]` authorization attribute used by the update endpoint, allowing any authenticated user (or potentially anonymous users, depending on global authorization) to delete invoices.  
  **Confidence:** High

## case-06
No defects found in the provided diff.

## case-07
- **File:** `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`  
  **Line:** 33–35  
  **Issue:** Logs the full invoice payload and current user/session object, potentially exposing sensitive financial or authentication/PII data in application logs.  
  **Confidence:** High

## case-08
- `.../InvoiceApp.Api/InMemoryInvoiceRepository.cs:9` — Replacing `ConcurrentDictionary` with `Dictionary` makes repository reads and writes unsafe under concurrent requests, potentially causing races, exceptions, or corrupted state. **Confidence: High.**
- `.../InvoiceApp.Api/InMemoryInvoiceRepository.cs:18-23` — `ContainsKey` followed by assignment is not atomic; concurrent `Add` calls for the same ID can both pass the check, so duplicate invoices may be silently accepted instead of throwing. **Confidence: High.**

## case-09
- **README.md:25** — The instruction to reset sample data by signing out and signing in again contradicts the preceding statement that data is recreated “on every start.” Unless authentication explicitly rebuilds the in-memory store, sign-out/sign-in will not reset data. **Confidence: High**

## case-10
Finding:
- `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs:34` — The new catch-all `Exception` handler converts every unexpected failure into HTTP 200 with `"completed"`, masking server errors and misleading clients that the operation succeeded. Confidence: High.

## case-11
- **`src/InvoiceApp.Api/Clients/PayExClient.cs:16-22`** — A new `HttpClient` is created for every submission and never disposed. This can exhaust sockets and cause connection failures under load. **Confidence: High**

- **`src/InvoiceApp.Api/Controllers/ApprovalsController.cs:37-38`** — The invoice is approved before the PayEx submission. If PayEx fails, the endpoint returns an error while the invoice remains approved, and retrying may be rejected or create inconsistent payment state. **Confidence: High**

## case-12
No defects found in the provided diff.
