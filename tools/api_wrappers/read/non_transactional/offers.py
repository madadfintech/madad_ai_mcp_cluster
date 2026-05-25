from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


class MadadOffersNonTransactionalReadAPI:
    """Read-only Madad offer endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def get_my_offers(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/offers/my-offers", bearer_token=access_token)

    async def get_offer(self, *, access_token: str, offer_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", f"/offers/{offer_id}", bearer_token=access_token)

    async def get_offers(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/offers", bearer_token=access_token)

    async def get_extension_request(self, *, access_token: str, offer_id: str) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            f"/offers/extension-request/{offer_id}",
            bearer_token=access_token,
        )
