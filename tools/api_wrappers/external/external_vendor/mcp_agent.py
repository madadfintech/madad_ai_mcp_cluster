from typing import Any, Dict, Optional

from shared.config import settings
from tools.api_wrappers.madad_client import MadadAPIClient, MadadAPIError


class MadadMCPAgentAPI:
    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    def _headers(self) -> Dict[str, str]:
        if not settings.MADAD_MCP_AGENT_SECRET:
            raise MadadAPIError("MADAD_MCP_AGENT_SECRET is required for MCP agent tools")
        return {"x-mcp-agent-secret": settings.MADAD_MCP_AGENT_SECRET}

    async def create_channel_session(
        self,
        *,
        channel: str,
        identifier: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        display_name: Optional[str] = None,
        create_onboarding_token: bool = True,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/mcp-agent/channel-sessions",
            json_body={
                "channel": channel,
                "identifier": identifier,
                "email": email,
                "phone": phone,
                "displayName": display_name,
                "createOnboardingToken": create_onboarding_token,
            },
            extra_headers=self._headers(),
        )

    async def get_webhook_events(self) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            "/mcp-agent/webhooks/events",
            extra_headers=self._headers(),
        )

    async def emit_webhook(
        self,
        *,
        event: str,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/mcp-agent/webhooks/emit",
            json_body={
                "event": event,
                "userId": user_id,
                "correlationId": correlation_id,
                "payload": payload or {},
            },
            extra_headers=self._headers(),
        )
