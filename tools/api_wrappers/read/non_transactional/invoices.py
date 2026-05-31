from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


class MadadInvoicesNonTransactionalReadAPI:
    """Read-only Madad invoice endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def get_my_invoices(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            "/invoices",
            bearer_token=access_token,
        )
