# Changed-variable run 2 (prompt v2) - raw reviewer outputs

Same setup as run 1 (see `variant-run1.md`). Verbatim.

## case-01
- **`backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs:49`** — `BulkApproveRequest.Ids` is nullable, but is enumerated without a null check. A request body with omitted or `null` `ids` causes `NullReferenceException`, producing an HTTP 500 instead of a validation error. **Confidence: high.**

## case-02
- **`backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:31,35`** — `customer` and `status` are interpolated directly into SQL. A request such as `GET /search?customer=' OR 1=1 --` changes the `WHERE` clause and returns invoices belonging to other customers; similarly, `status` can inject additional SQL. **Confidence: high.**

## case-03
- **`backend/src/InvoiceApp.Domain/DiscountCalculator.cs:16-17`** — The calculation now truncates both the discount and final amount toward zero, changing expected rounding. For example, `Apply(100m, 12.346m)` returns `87.66m`, whereas rounding the final discounted amount away from zero returns `87.65m`. **Confidence: high**

## case-04
No defects found.

## case-05
- **`backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs:44-49`** — `Delete` lacks the `[RequireRole("Admin")]` authorization attribute present on `Update`. A non-admin authenticated caller who invokes `DELETE /{id}` can delete an invoice, with a successful `204 No Content` response. **Confidence: High**

## case-06
No defects found.

## case-07
Finding:

- **File:** `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`
- **Line:** 34
- **Defect:** The approval endpoint logs the full invoice payload and current user/session object. If either contains sensitive invoice data, credentials, tokens, or personal information, every successful approval writes that data to application logs, exposing it to anyone with log access and potentially violating data-minimization requirements.
- **Confidence:** High

## case-08
- **`backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs:9,18-25`** — Replacing `ConcurrentDictionary` with `Dictionary` makes repository operations unsafe under concurrent requests. For example, two concurrent `Add` calls with the same ID can both pass `ContainsKey` and then overwrite each other instead of one throwing; simultaneous reads/writes can also produce lost updates or runtime failures. **Confidence: high**

## case-09
No defects found.

## case-10
- **`backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs:35-38`** — The broad `catch (Exception)` converts any unexpected failure (for example, a database outage) into HTTP 200 with `{"status":"completed"}`. Clients observe a successful completion despite the operation failing, and the exception is suppressed. **Confidence: High**

## case-11
- **`src/InvoiceApp.Api/Clients/PayExClient.cs:17–21`** — A new `HttpClient` is created for every submission and never disposed. Repeated invoice approvals can exhaust sockets/connections, causing later PayEx requests to fail with connection/resource errors. **Confidence: High**

- **`src/InvoiceApp.Api/Controllers/ApprovalsController.cs:38–39`** — The invoice is approved before the PayEx submission. If PayEx accepts the payment but the request times out or returns an error, the API reports failure while the invoice remains approved; retrying approval can submit the same payment again. **Confidence: High**

## case-12
No defects found in the provided diff.
