from typing import Any, Dict, Optional

from tools.api_wrappers.external.external_vendor import MadadMCPAgentAPI

from . import mcp


mcp_agent_api = MadadMCPAgentAPI()


@mcp.tool
async def madad_mcp_create_channel_session(
    channel: str,
    identifier: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    display_name: Optional[str] = None,
    create_onboarding_token: bool = True,
    create_user_if_missing: bool = False,
) -> Dict[str, Any]:
    """Create a scoped Madad channel session for a WhatsApp or email identity.

    For WhatsApp, set create_user_if_missing=True when the lead has just shown intent
    (replied YES). The backend then creates a SIGN_UP account immediately from the
    phone number — no email, no password — and returns an access token you can use
    right away for document uploads. The response distinguishes:
      - sessionType "new_user_created" : a fresh lead was created (use accessToken).
      - sessionType "existing_user"    : a WhatsApp lead is resuming (whatsappOnboardingStep tells you where).
      - sessionType "existing_portal_user" (requiresPortalLogin=true) : a portal user
        already exists for this number — tell them their application exists and to log in.
    """
    return await mcp_agent_api.create_channel_session(
        channel=channel,
        identifier=identifier,
        email=email,
        phone=phone,
        display_name=display_name,
        create_onboarding_token=create_onboarding_token,
        create_user_if_missing=create_user_if_missing,
    )


@mcp.tool
async def madad_mcp_check_registration(
    identifier: str,
    channel: str = "WHATSAPP",
    email: Optional[str] = None,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    """Read-only check of whether a phone/email is already registered, with the
    journey state needed to route a "YES" reply. Never creates anything — call this
    BEFORE madad_mcp_create_channel_session to decide what to send.

    Returns `registered` (bool). When registered, use `route` to decide the message:
      - 'portal_login_required'       : portal-only account → ask them to log in.
      - 'invoice_discounting'         : credit line is ACTIVE → invite invoice upload right now.
      - 'offer_accepted_confirmation' : they already accepted an offer → send the confirmation message.
      - 'offers_available'            : ≥1 offer has been made → re-send the offer(s) with details (see `offers`).
      - 'payment_received'            : QUALIFIED + onboarding fee paid → "payment received, lenders reviewing" message.
      - 'payment_link'                : QUALIFIED + fee unpaid → re-send Madad score + payment link.
      - 'continue_step'               : resume whichever onboarding step they're at (see whatsappOnboardingStep).
    Also returns: whatsappOnboarding, whatsappOnboardingStep, journeyStatus, onboardingFeePaid,
    creditLineActive, creditLine {creditLimit, interestRate, tenureDays, currency}, offerAccepted,
    hasPendingOffers, offers [{lenderName, creditLimit, interestRate, tenureDays, processingFeeType,
    processingFeeValue, status, currency}], userId, referenceNumber.
    """
    return await mcp_agent_api.lookup_identity(
        identifier=identifier,
        channel=channel,
        email=email,
        phone=phone,
    )


@mcp.tool
async def madad_mcp_set_business_email(
    email: str,
    user_id: Optional[str] = None,
    channel: Optional[str] = "WHATSAPP",
    identifier: Optional[str] = None,
) -> Dict[str, Any]:
    """Attach the lead's BUSINESS email — the step right after they say YES and
    the account is created. Call this once the lead replies with their email.

    Identify the lead by user_id, or by channel + identifier (phone).

    Returns {ok, conflict, ...}:
      - conflict=false, ok=true  : email attached → proceed to the CR-number step.
      - conflict=true            : a business is ALREADY registered with this email.
                                   Offer two buttons: "Add a different email"
                                   (call this tool again with the new email) or
                                   "Contact support".
      - alreadyPortalUser=true   : this number already has a portal account → ask
                                   them to log in instead.
    Attaching the email also makes the lead a normal, portal-loginable user.
    """
    return await mcp_agent_api.set_business_email(
        email=email,
        user_id=user_id,
        channel=channel,
        identifier=identifier,
    )


@mcp.tool
async def madad_mcp_update_onboarding_progress(
    user_id: Optional[str] = None,
    channel: Optional[str] = None,
    identifier: Optional[str] = None,
    step: Optional[int] = None,
    touch_inbound: bool = False,
) -> Dict[str, Any]:
    """Record WhatsApp onboarding progress for a lead.

    Set `step` to the conversational step the lead has reached so backend gates work —
    in particular set step=3 once the lead has submitted their financials and you've
    sent the "pre-qualification within 24 hours / account created" message, because the
    backend only fires the pre-qualified document checklist for leads at step >= 3.
    Set touch_inbound=True whenever the lead messages you, to keep Meta's 24h window
    fresh. Identify the lead by user_id, or by channel + identifier (phone).
    """
    return await mcp_agent_api.update_onboarding_progress(
        user_id=user_id,
        channel=channel,
        identifier=identifier,
        step=step,
        touch_inbound=touch_inbound,
    )


@mcp.tool
async def madad_mcp_get_onboarding_progress(
    user_id: Optional[str] = None,
    channel: Optional[str] = None,
    identifier: Optional[str] = None,
) -> Dict[str, Any]:
    """Read a WhatsApp lead's current onboarding step, last-inbound time and journey
    status. Identify the lead by user_id, or by channel + identifier (phone)."""
    return await mcp_agent_api.get_onboarding_progress(
        user_id=user_id,
        channel=channel,
        identifier=identifier,
    )


@mcp.tool
async def madad_mcp_get_webhook_events() -> Dict[str, Any]:
    """List backend event names supported for agent webhooks."""
    return await mcp_agent_api.get_webhook_events()


@mcp.tool
async def madad_mcp_emit_webhook(
    event: str,
    channel: Optional[str] = None,
    identity: Optional[str] = None,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Emit a backend-to-agent webhook event using the configured backend webhook target."""
    return await mcp_agent_api.emit_webhook(
        event=event,
        channel=channel,
        identity=identity,
        user_id=user_id,
        correlation_id=correlation_id,
        payload=payload,
    )
