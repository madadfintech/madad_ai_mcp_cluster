from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


class MadadKYCNonTransactionalReadAPI:
    """Read-only Madad KYC endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def get_documents(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/documents", bearer_token=access_token)

    async def get_business_documents(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/business-documents", bearer_token=access_token)

    async def get_financial_documents(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/financial-documents", bearer_token=access_token)

    async def get_admin_requested_documents(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/admin-requested-documents", bearer_token=access_token)

    async def get_business_details(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/business-details", bearer_token=access_token)

    async def get_shareholders(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/shareholders", bearer_token=access_token)

    async def get_shareholders_kyc_status(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/shareholders-kyc-status", bearer_token=access_token)

    async def get_shareholders_consents(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/shareholders-consents", bearer_token=access_token)

    async def get_buyers(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/buyers", bearer_token=access_token)

    async def get_primary_bank_detail(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/kyc/primary-bank-detail", bearer_token=access_token)
