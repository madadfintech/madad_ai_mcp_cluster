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
- Payment tools call admin/ops backend endpoints and require an `ADMIN`, `OPS`, or `SUPER_ADMIN` access token.
- MCP should never receive or store Meta, TESS, SMS, email-provider, or database credentials.

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

### WhatsApp

Use only:

- `madad_external_send_whatsapp_text`
- `madad_external_send_whatsapp_template`

The backend owns WhatsApp credentials and Meta API calls.

### TESS Payment Gate

Payment integration is implemented in the backend `payments` module. MCP exposes the payment gate through backend-only tools:

- `madad_payments_search_businesses`
- `madad_payments_list_monetization_products`
- `madad_payments_create_monetization_payment`
- `madad_payments_send_monetization_payment_link`
- `madad_payments_get_monetization_payment`
- `madad_payments_list_monetization_payments`
- `madad_payments_sync_monetization_payment_status`
- `madad_payments_get_collection_reports`

Preferred Step 5 payment flow:

```text
madad_payments_search_businesses -> businessDetailsId
madad_payments_list_monetization_products -> productId
madad_payments_create_monetization_payment -> paymentLink + paymentId
madad_payments_send_monetization_payment_link -> sends link by backend email/SMS
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
