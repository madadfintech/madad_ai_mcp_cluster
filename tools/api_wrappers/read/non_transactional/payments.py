from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


def compact_params(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


class MadadPaymentsNonTransactionalReadAPI:
    """Read-only Madad payment and monetization endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def search_businesses(
        self,
        *,
        access_token: str,
        search: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            "/payments/businesses",
            params=compact_params(search=search, limit=limit),
            bearer_token=access_token,
        )

    async def list_monetization_products(
        self,
        *,
        access_token: str,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            "/payments/monetization-products",
            params=compact_params(search=search, status=status),
            bearer_token=access_token,
        )

    async def list_monetization_payments(
        self,
        *,
        access_token: str,
        business_details_id: Optional[str] = None,
        product_id: Optional[str] = None,
        internal_status: Optional[str] = None,
        provider_status: Optional[str] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            "/payments/monetization-payments",
            params=compact_params(
                businessDetailsId=business_details_id,
                productId=product_id,
                internalStatus=internal_status,
                providerStatus=provider_status,
                search=search,
                page=page,
                pageSize=page_size,
            ),
            bearer_token=access_token,
        )

    async def get_monetization_payment(self, *, access_token: str, payment_id: str) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            f"/payments/monetization-payments/{payment_id}",
            bearer_token=access_token,
        )

    async def get_collection_reports(
        self,
        *,
        access_token: str,
        business_details_id: Optional[str] = None,
        product_id: Optional[str] = None,
        internal_status: Optional[str] = None,
        provider_status: Optional[str] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "GET",
            "/payments/collection-reports",
            params=compact_params(
                businessDetailsId=business_details_id,
                productId=product_id,
                internalStatus=internal_status,
                providerStatus=provider_status,
                search=search,
                page=page,
                pageSize=page_size,
            ),
            bearer_token=access_token,
        )
