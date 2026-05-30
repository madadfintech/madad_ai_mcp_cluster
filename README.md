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

## Final Agent Flow Contract

1. Resolve the WhatsApp/email identity with `madad_mcp_create_channel_session`.
2. If the response has `sessionType: "existing_user"`, use the returned `accessToken` as `access_token` in protected KYC/offer/status tools.
3. If the response has `sessionType: "new_lead"`, use the returned `onboardingToken` only for onboarding tools.
4. After `madad_auth_complete_onboarding` creates the user, call `madad_mcp_create_channel_session` again for the same verified channel identity. The second call returns the `accessToken` needed for protected KYC/offer/status tools.
5. Upload WhatsApp/email documents with `madad_kyc_upload_document_base64`.
6. Use `madad_auth_me` only for explicit status checks while backend webhooks are being wired.
7. Use offer tools only to view offers. Final offer acceptance/signing stays on the Madad platform.

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

### WhatsApp

Use only:

- `madad_external_send_whatsapp_text`
- `madad_external_send_whatsapp_template`

The backend owns WhatsApp credentials and Meta API calls.

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
