# Agent Integration TODOs

These are additive integration items for the agentic WhatsApp/email journey.

## Backend Status Webhooks

- Add backend outbound webhooks for journey events instead of requiring the agent to poll `/auth/me`.
- Suggested events: `eligibility.updated`, `documents.completed`, `prequalification.completed`, `madad_score.ready`, `payment.completed`, `offers.available`, `offer.accepted`, `credit_line.activated`.
- Use an outbox table, retries, signed payloads, idempotency keys, and dead-letter handling.

## Offer And Credit-Line Events

- Keep offer acceptance and legal lender selection on the Madad platform.
- Emit signed backend webhooks to the agent for offer availability, offer acceptance, and credit-line activation.

## Tess Payments

- Finish the backend `feat/tess_payments` branch.
- Payment link creation and Tess webhook verification should stay in backend/portal, not MCP.
- Emit a backend event to the agent after payment success/failure.

## MCP Transport Auth

- Restrict production MCP Cloud Run with IAM so only the internal agent service account can invoke it.
- Add an optional signed request header from agent to MCP and verify it at the MCP edge.
- Add IP allowlisting or Cloud Armor rules where applicable.

## Channel Sessions

- Add a new backend channel-session layer for WhatsApp/email identities.
- Verified WhatsApp/email webhooks should resolve the channel to a Madad user or provisional lead.
- Mint short-lived, scoped agent action tokens or execute channel-authorized actions server-side.
- Do not change or weaken the existing portal cookie auth flow.

## Idempotency

- Add `Idempotency-Key` support for document uploads, status updates, payment callbacks, offer callbacks, and outbound webhooks.
- Store request hashes and response references to make retries safe.
