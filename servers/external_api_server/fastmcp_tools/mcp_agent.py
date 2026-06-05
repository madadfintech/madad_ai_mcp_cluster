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
) -> Dict[str, Any]:
    """Create a scoped Madad channel session for a verified WhatsApp or email identity."""
    return await mcp_agent_api.create_channel_session(
        channel=channel,
        identifier=identifier,
        email=email,
        phone=phone,
        display_name=display_name,
        create_onboarding_token=create_onboarding_token,
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
