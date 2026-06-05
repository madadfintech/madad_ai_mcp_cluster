# Madad MCP Cluster

FastMCP server for the Madad agentic onboarding tools. The MCP cluster does not call external vendors directly; it calls the Madad backend, and the backend owns platform auth, WhatsApp, email, SMS, KYC, offers, and payment integrations.

## Deployed MCP URL

```text
https://madad-mcp-cluster-626656664233.me-central1.run.app/mcp
```

FastMCP uses JSON-RPC over HTTP/SSE. Postman requests must include:

```http
Content-Type: application/json
Accept: application/json, text/event-stream
Authorization: Bearer <MCP__AUTH_TOKEN>
```

## Required Runtime Environment

```bash
MADAD_API_BASE_URL=https://uat-api.madadfintech.com
MADAD_API_TIMEOUT=30
MADAD_MCP_AGENT_SECRET=<same value as backend MCP_AGENT_SHARED_SECRET>
```

The MCP cluster should not contain Meta/WhatsApp tokens. WhatsApp messages are sent through backend tools only.

## Calling Tools

Every tool is called through the FastMCP JSON-RPC endpoint:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "method": "tools/call",
  "params": {
    "name": "madad_auth_me",
    "arguments": {
      "access_token": "<token>"
    }
  }
}
```

To list the available tools:

```json
{
  "jsonrpc": "2.0",
  "id": "tools-list",
  "method": "tools/list",
  "params": {}
}
```

## Final Agent Flow Contract

1. Resolve the WhatsApp/email identity with `madad_mcp_create_channel_session`.
2. If the response has `sessionType: "existing_user"`, use the returned `accessToken` as `access_token` in protected KYC/offer/status tools.
3. If the response has `sessionType: "new_lead"`, use the returned `onboardingToken` only for onboarding tools.
4. After `madad_auth_complete_onboarding` creates the user, call `madad_mcp_create_channel_session` again for the same verified channel identity. The second call returns the `accessToken` needed for protected KYC/offer/status tools.
5. Upload WhatsApp/email documents with `madad_kyc_upload_document_base64`.
6. Use `madad_auth_me` only for explicit status checks while backend webhooks are being wired.
7. Use offer tools only to view offers. Final offer acceptance/signing stays on the Madad platform.

## Token Rules

- `onboardingToken` is only for onboarding endpoints such as `madad_auth_complete_onboarding`.
- `accessToken` is for protected KYC, offer, status, and user-facing tools.
- Payment tools can be called with the user's access token through MCP. MCP adds the backend-only shared secret header, and the backend allows only the marked payment-gate routes.
- MCP payment write tools require an `idempotency_key`. Reuse the same key when retrying the same create/send action.
- MCP should never receive or store Meta, TESS, SMS, email-provider, or database credentials.

## Exact MCP Argument Types

All MCP tools are called through JSON-RPC `tools/call` at `/mcp`. Use JSON-native types exactly as listed below. Do not pass empty strings for optional IDs, phone numbers, or email fields; use `null` when a value is intentionally absent.

### `madad_mcp_emit_webhook`

Used for smoke-testing the backend-to-agent webhook path.

```json
{
  "event": "eligibility.updated",
  "channel": "email",
  "identity": "tech.external1@madadfintech.com",
  "user_id": null,
  "correlation_id": "postman-test-001",
  "payload": {
    "source": "postman"
  }
}
```

Arguments:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `event` | `string` | Yes | One supported event name from `madad_mcp_get_webhook_events`. |
| `channel` | `string \| null` | No | `email`, `whatsapp`, `EMAIL`, or `WHATSAPP`. |
| `identity` | `string \| null` | No | Email address or E.164/WhatsApp phone for the agent session. |
| `user_id` | `string \| null` | No | Backend user ID if already known. |
| `correlation_id` | `string \| null` | No | Trace/request ID for debugging. |
| `payload` | `object \| null` | No | Event-specific JSON object. |

### `madad_kyc_upload_document_base64`

Used for WhatsApp/email document bytes. The `base64` value must be raw base64 only, without a `data:` URL prefix.

```json
{
  "file_name": "CR_Company.pdf",
  "mime_type": "application/pdf",
  "base64": "BASE64_FILE_BYTES_HERE",
  "metadata": {
    "access_token": "<access token>",
    "document_entity_type": "BUSINESS_DETAILS",
    "document_type": "COMMERCIAL_REGISTRATION",
    "kyc_stage": "Business Documents",
    "document_param": null,
    "document_label": null,
    "from_admin": false,
    "target_user_id": null
  }
}
```

Arguments:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `file_name` | `string` | Yes | Original file name, including extension. |
| `mime_type` | `string \| null` | No | Example: `application/pdf`, `image/jpeg`, `image/png`, `application/zip`. |
| `base64` | `string` | Yes | Raw file bytes encoded as base64. |
| `metadata` | `object` | Yes | Backend upload metadata. |
| `metadata.access_token` | `string` | Yes | Scoped backend access token. |
| `metadata.document_entity_type` | `string` | Yes | For CR/financials use `BUSINESS_DETAILS`. Other valid values include `KYC`, `SHAREHOLDER`, `DIRECTOR`, `BUYER`, `INVOICE`, `OFFER`, `TICKET`, `COMMUNICATION`, `BANK_DETAILS`, `AUTH_SIGNATORY`, `BENEFICIAL_OWNER`, and `USER`. |
| `metadata.document_type` | `string` | Yes | For CR use `COMMERCIAL_REGISTRATION`; for audited financials use `AUDITED_FINANCIAL_REPORT`. |
| `metadata.kyc_stage` | `string \| null` | No | Example: `Business Documents` or `Financial Documents`. |
| `metadata.document_param` | `string \| null` | No | Optional label/year/parameter when required by backend document rules. |
| `metadata.document_label` | `string \| null` | No | Optional display label. |
| `metadata.from_admin` | `boolean` | No | Default `false`. |
| `metadata.target_user_id` | `string \| null` | No | Only for admin-style targeted upload flows. |

Common document types used in the agent flow:

- `COMMERCIAL_REGISTRATION`
- `AUDITED_FINANCIAL_REPORT`
- `TRADE_LICENSE`
- `TAX_CARD`
- `ESTABLISHMENT_CARD`
- `ARTICLE_OF_ASSOCIATION`
- `MEMORANDUM_OF_ASSOCIATION`
- `COMMERCIAL_CREDIT_REPORT`
- `PAYABLE_AGING_REPORT`
- `RECEIVABLES_AGING_REPORT`
- `INTERIM_FINANCIAL_REPORT`
- `BANK_STATEMENT`
- `SHAREHOLDER_QID`
- `SHAREHOLDER_PASSPORT`
- `SHAREHOLDER_PROOF_OF_ADDRESS`
- `INVOICE_FILE`
- `INVOICE_SUPPORTING_DOCUMENT`

### WhatsApp Tools

`madad_external_send_whatsapp_text`

```json
{
  "to": "919497191690",
  "body": "Madad WhatsApp test message.",
  "preview_url": false
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `to` | `string` | Yes | Recipient phone in E.164/digits format, without spaces. |
| `body` | `string` | Yes | Text message body. |
| `preview_url` | `boolean` | No | Default `false`. |

`madad_external_send_whatsapp_template`

```json
{
  "to": "919497191690",
  "template_name": "hello_world",
  "language_code": "en_US",
  "components": null
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `to` | `string` | Yes | Recipient phone in E.164/digits format, without spaces. |
| `template_name` | `string` | Yes | Approved Meta template name. |
| `language_code` | `string` | No | Example: `en_US`; defaults depend on backend/template. |
| `components` | `array<object> \| null` | No | Meta template components. Use `null` for templates without variables. |

MCP does not call Meta directly. The backend owns the WhatsApp phone number ID, WABA ID, and access token.

### `madad_payments_send_monetization_payment_link`

```json
{
  "access_token": "<access token>",
  "payment_id": "<payment id>",
  "recipient_email": "tech.external1@madadfintech.com",
  "recipient_phone": null,
  "message_title": "Madad onboarding payment",
  "message_body": "Please complete your Madad onboarding and assessment fee payment using this secure link.",
  "idempotency_key": "run-123:madad_payments_send_monetization_payment_link:1"
}
```

Arguments:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `access_token` | `string` | Yes | Scoped backend access token. |
| `payment_id` | `string` | Yes | ID returned by `madad_payments_create_monetization_payment`. |
| `recipient_email` | `string \| null` | No | Use `null` if sending only to phone. |
| `recipient_phone` | `string \| null` | No | Use `null` if sending only to email. |
| `message_title` | `string \| null` | No | Optional notification title. |
| `message_body` | `string \| null` | No | Optional notification body. |
| `idempotency_key` | `string` | Yes | Reuse the same key for retrying the same send action. |

## Core Tools

### Channel Session

`madad_mcp_create_channel_session(channel, identifier, email, phone, display_name, create_onboarding_token)`

- `channel`: `WHATSAPP` or `EMAIL`
- `identifier`: WhatsApp phone number or email address from the verified channel
- Returns an `accessToken` for existing users or an `onboardingToken` for new leads.

For new leads, the handoff sequence is:

```text
madad_mcp_create_channel_session -> onboardingToken
madad_auth_complete_onboarding -> creates user/business
madad_mcp_create_channel_session -> accessToken
```

Do not use an onboarding token for KYC document uploads.

### Document Upload

`madad_kyc_upload_document_base64(file_name, mime_type, base64, metadata)`

Required metadata:

```json
{
  "access_token": "<scoped access token>",
  "document_entity_type": "BUSINESS_DETAILS",
  "document_type": "COMMERCIAL_REGISTRATION",
  "kyc_stage": "Business Documents"
}
```

Use this for CR, audited financial reports, and documents received over WhatsApp/email. Do not pass arbitrary file paths in production.

### Eligibility and Status

- `madad_kyc_update_eligibility`
- `madad_auth_me`
- `madad_kyc_get_business_details`

The agent should use the explicit step APIs for progression. `madad_auth_me` is the fallback status read and returns the current user state, including `journeyStatus`.

#### Journey Status Reference

`madad_auth_me` returns `user.journeyStatus`. Use this value to answer user status questions and decide the next conversational step when a webhook is not available.

Queue terminology:

- Verification: Ops Queue
- Qualification: Credit Queue
- Validation: Buyer Queue
- Acceptance: Lender Queue

Canonical backend statuses:

| Status | Meaning for the agent |
| --- | --- |
| `SIGN_UP` | User has signed up but has not checked eligibility yet. |
| `ONBOARDED` | User account/onboarding record exists, but the KYC/application journey has not meaningfully progressed yet. Treat as early onboarding and continue with eligibility/document collection as needed. |
| `IN_ELIGIBLE` | User checked eligibility and was marked ineligible. |
| `ELIGIBLE` | User checked eligibility and was marked eligible. |
| `INCOMPLETE` | Eligible user has reached the document submission stage and may have uploaded zero or more documents, but the required document set is not complete yet. |
| `UNVERIFIED` | User uploaded all required documents, but Madad Ops has not verified at least one document yet. Also used when Credit sends the application back for document correction or re-verification. |
| `VERIFIED` | Madad Ops has verified the documents and the application is open for credit assessment. |
| `PRE_QUALIFIED` | User has passed the initial pre-qualification step and should continue toward full document submission/payment flow as applicable. |
| `QUALIFIED` | Madad Credit has qualified the user and the application is being sent to financial institutions. |
| `UNQUALIFIED` | Madad Credit reviewed the user and rejected the application, so it is not sent to financial institutions. |
| `ACCEPTED` | Financial institution accepted the application and the user is ready for contract signatures and disbursal steps. |
| `NOT_ACCEPTED` | Financial institutions rejected the application. |
| `OFFER_ACCEPTED` | User accepted an offer from one financial institution on the Madad platform. |
| `OFFER_EXPIRED` | User has at least one expired offer. |
| `OPEN` | More information is needed by Madad or the lender. The agent should ask for or route the missing information based on the latest document/status context. |
| `ACTIVATED` | User's accepted offer/credit line is activated. The user can proceed with invoice financing workflows. |

### Document Checklist

- `madad_kyc_get_documents`
- `madad_kyc_get_business_documents`
- `madad_kyc_get_financial_documents`
- `madad_kyc_get_admin_requested_documents`

These tools let the agent answer "what is missing?" and keep the Step 4 checklist synchronized.

### Shareholders and Buyers

Shareholder tools:

- `madad_kyc_add_shareholders`
- `madad_kyc_get_shareholders`
- `madad_kyc_update_shareholder`
- `madad_kyc_delete_shareholder`
- `madad_kyc_upload_shareholder_documents`

Buyer/paymaster tools:

- `madad_kyc_add_buyer`
- `madad_kyc_edit_buyer`
- `madad_kyc_get_buyers`
- `madad_kyc_delete_buyer`

### Invoice Financing

Invoice tools mirror the MSME portal's `/invoices/upload` workflow:

- `madad_invoices_extract_invoice`
- `madad_invoices_extract_invoice_base64`
- `madad_invoices_submit_invoice`
- `madad_invoices_submit_invoice_base64`
- `madad_invoices_extract_and_submit_invoice`
- `madad_invoices_extract_and_submit_invoice_base64`
- `madad_invoices_inspect_zip`
- `madad_invoices_upload_zip`
- `madad_invoices_get_my_invoices`

For WhatsApp/email attachments, use `madad_invoices_extract_and_submit_invoice_base64` when the agent should assume extracted data is correct and submit immediately. For ZIPs, `madad_invoices_upload_zip` extracts each file and recursively runs the same invoice upload flow.

### WhatsApp

Use only:

- `madad_external_send_whatsapp_text`
- `madad_external_send_whatsapp_template`

The backend owns WhatsApp credentials and Meta API calls.

### TESS Payment Gate

Payment integration is implemented in the backend `payments` module. MCP exposes the payment gate through backend-only tools:

- `madad_payments_list_monetization_products`
- `madad_payments_create_monetization_payment`
- `madad_payments_send_monetization_payment_link`
- `madad_payments_get_monetization_payment`
- `madad_payments_sync_monetization_payment_status`

Preferred Step 5 payment flow:

```text
madad_kyc_get_business_details -> businessDetailsId
madad_payments_list_monetization_products -> productId
madad_payments_create_monetization_payment(idempotency_key) -> paymentLink + paymentId
madad_payments_send_monetization_payment_link(idempotency_key) -> sends link by backend email/SMS
TESS callback hits backend -> backend updates payment status
madad_payments_get_monetization_payment or webhook -> read status
```

Use `madad_payments_create_monetization_payment` for the QAR 6,000 onboarding and assessment fee because it always creates a durable backend payment record and a TESS checkout link together.

### Webhooks

Supported backend-to-agent event names are exposed by `madad_mcp_get_webhook_events`.

Initial event names:

- `eligibility.updated`
- `documents.completed`
- `prequalification.completed`
- `madad_score.ready`
- `payment.completed`
- `offers.available`
- `offer.accepted`
- `credit_line.activated`
- `transaction.disbursed`
- `repayment.received`
- `repayment.partially_paid`
- `repayment.closed`
- `repayment.due_soon`
- `repayment.overdue`

`madad_mcp_emit_webhook` is available as a test/smoke tool. Production service methods can call the backend `McpAgentService.emitWebhook` internally when each business event is finalized.

## Agentic Journey Mapping

### Step 1: Interest, Consent, CR Request

Use WhatsApp/email tools through the backend for communication. Resolve identity with `madad_mcp_create_channel_session`. For new leads, complete onboarding after collecting the minimum CR-derived details needed by backend onboarding.

### Step 2: CR Upload and Eligibility

Use `madad_kyc_upload_document_base64` for CR bytes from WhatsApp/email. Then use `madad_kyc_update_eligibility` once the agent has the eligibility answers.

### Step 3: Audited Financial Report

Use `madad_kyc_upload_document_base64` with `document_type: "AUDITED_FINANCIAL_REPORT"` and a suitable `document_param` such as the financial year.

### Step 4: Full Document Submission

Use the document checklist read tools, buyer/paymaster tools, shareholder tools, and `madad_kyc_upload_document_base64`. ZIP classification is an agent workflow concern; the agent should extract/classify files and call the upload tool for each mapped document.

### Step 5: Risk Assessment and Payment Gate

Risk scoring remains backend/admin driven. Once payment is required, use the TESS payment tools above to create and send the onboarding fee link.

### Step 6: Payment Confirmation

TESS sends the callback to the backend. The backend updates the monetization payment record. The agent can read status with `madad_payments_get_monetization_payment` or receive the future `payment.completed` webhook.

### Step 7: Lender Evaluation

Use `madad_auth_me` only for user-requested status checks until backend event webhooks are wired into status-changing service methods.

### Step 8: Offer Marketplace Preview

Use offer read tools only:

- `madad_offers_get_my_offers`
- `madad_offers_get_offer`

Final offer selection, acceptance, and signing stay on the Madad platform.

### Step 10: Invoice Submission

Use the invoice tools above. The default agent path is:

```text
madad_invoices_extract_and_submit_invoice_base64 -> submitted invoice
madad_invoices_get_my_invoices -> user invoice list/status
```

For bulk invoice ZIPs, use `madad_invoices_upload_zip`. It extracts the ZIP locally in MCP and uploads each invoice through the backend `/invoices/upload` API. If a future human review CSV is required, that should be added as a separate backend/agent workflow.

## Local Run

```bash
source venv/bin/activate
MADAD_API_BASE_URL=http://127.0.0.1:8080 \
MADAD_MCP_AGENT_SECRET=<shared secret> \
PORT=8011 \
python -m servers.external_api_server.fastmcp_main
```

Health:

```bash
curl http://127.0.0.1:8011/health
```

Tool catalogue:

```bash
curl http://127.0.0.1:8011/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```
