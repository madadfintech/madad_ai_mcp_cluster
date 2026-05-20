from typing import Dict, Optional, Any

from tools.api_wrappers.common import MadadAPIClient


class MadadAuthExternalVendorAPI:
    """Madad auth endpoints that start external OAuth flows."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def google_oauth_url(self) -> Dict[str, Any]:
        return await self.client.request("GET", "/auth/google")

    async def google_callback(self) -> Dict[str, Any]:
        return await self.client.request("GET", "/auth/google/callback")
