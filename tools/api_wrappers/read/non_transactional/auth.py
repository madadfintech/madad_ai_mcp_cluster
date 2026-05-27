from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


def compact_payload(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


class MadadAuthReadAPI:
    """Read-only Madad auth endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def check_contact(
        self,
        *,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/check-contact",
            json_body=compact_payload(phone=phone, email=email),
        )

    async def me(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/auth/me", bearer_token=access_token)
