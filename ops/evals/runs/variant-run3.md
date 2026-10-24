# Changed-variable run 3 (prompt v2) - raw reviewer outputs

Same setup as run 1 (see `variant-run1.md`). Verbatim.

## case-01
- **`backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs:50`** — `BulkApproveRequest.Ids` is nullable, but is enumerated without a null check. A request with a missing or `null` `ids` property causes `NullReferenceException`, yielding a server error instead of a client validation response. **Confidence: high.**

## case-02
- `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:27-33` — `customer` and `status` are interpolated directly into SQL. A request such as `?customer=' OR 1=1 --` can alter the `WHERE` clause and return all invoices; a crafted `status` can similarly inject SQL or execute additional statements depending on the database. **Confidence: high.**

## case-03
- **`backend/src/InvoiceApp.Domain/DiscountCalculator.cs:15`** — For `amount = 100` and `discountPercent = 12.349`, the method truncates the discount to `12.34`, returning `87.66`. Previously, the mathematically discounted amount `87.651` rounded away from zero to `87.65`. Thus the change can overstate the invoice total by `0.01`. **Confidence: High**

## case-04
No defects found.

## case-05
- **`backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:45-51`** — `Delete` has no `[RequireRole("Admin")]` authorization unlike `Update`. An authenticated non-admin user can send `DELETE /{id}`, causing `_repository.Delete(id)` to remove the invoice and receive `204 No Content`. **Confidence: High.**

## case-06
No defects found.

## case-07
- **`backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs:34-36`** — Every successful approval logs the complete invoice payload and `CurrentUser` object. If either contains sensitive invoice data, personal information, or session credentials, those values are persisted in application logs and exposed to anyone with log access. **Confidence: High**

## case-08
- `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs:8` — Replacing `ConcurrentDictionary` with `Dictionary` makes repository operations unsafe when requests access it concurrently. Concurrent reads/writes (for example, `Update` while `GetById` runs) can race, throw exceptions, or observe corrupted/inconsistent state. **Confidence: High.**

- `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs:18-23` — The `ContainsKey` check and subsequent assignment are not atomic. Two concurrent `Add` calls for the same invoice ID can both pass the check, then one silently overwrites the other instead of throwing the documented duplicate exception. **Confidence: High.**

## case-09
No defects found.

## case-10
Finding — `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs:34`

Catching every other exception and returning `200 OK` with `{"status":"completed"}` causes failed operations to appear successful. For any unexpected exception thrown by `action()`, clients receive a success response and cannot detect the failure; the exception is also swallowed. **Confidence: high.**

## case-11
- **`src/InvoiceApp.Api/Clients/PayExClient.cs:19-25`** — A new `HttpClient` is created for every submission and never disposed. Repeated approval requests can exhaust sockets/connections, causing later PayEx calls to fail with connection/resource errors. **Confidence: High**

- **`src/InvoiceApp.Api/Controllers/ApprovalsController.cs:38-39`** — The invoice is approved before `SubmitAsync` completes. If PayEx returns an error or times out, the endpoint returns failure while the invoice remains approved; retrying can also submit the same invoice again. **Confidence: High**

- **`src/InvoiceApp.Api/Contracts/DecisionResponse.cs:5-6`** — Renaming response properties from `DecidedBy`/`DecidedAt` to `ApprovedBy`/`ApprovedAt` breaks existing API consumers: deserializing the new response into the prior contract leaves the old fields unset. **Confidence: High**

## case-12
No defects found.
