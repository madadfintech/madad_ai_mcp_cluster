from typing import Any, Dict, List, Optional

from shared.config import settings
from tools.api_wrappers.common import MadadAPIClient


def compact_payload(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


class MadadPaymentsTransactionalWriteAPI:
    """Write-capable Madad payment and monetization endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    def _mcp_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if settings.MADAD_MCP_AGENT_SECRET:
            headers["x-mcp-agent-secret"] = settings.MADAD_MCP_AGENT_SECRET
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    async def create_monetization_payment(
        self,
        *,
        access_token: str,
        idempotency_key: str,
        business_details_id: str,
        product_id: str,
        payable_amount: Optional[float] = None,
        mode_of_payment: str = "CHECKOUT",
        operation: Optional[str] = "purchase",
        methods: Optional[List[str]] = None,
        session_expiry_minutes: Optional[int] = None,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/payments/monetization-payments",
            json_body=compact_payload(
                businessDetailsId=business_details_id,
                productId=product_id,
                payableAmount=payable_amount,
                modeOfPayment=mode_of_payment,
                operation=operation,
                methods=methods,
                sessionExpiryMinutes=session_expiry_minutes,
                recipientEmail=recipient_email,
                recipientPhone=recipient_phone,
                customData=custom_data,
            ),
            bearer_token=access_token,
            extra_headers=self._mcp_headers(idempotency_key),
        )

    async def send_monetization_payment_link(
        self,
        *,
        access_token: str,
        idempotency_key: str,
        payment_id: str,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        message_title: Optional[str] = None,
        message_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            f"/payments/monetization-payments/{payment_id}/send",
            json_body=compact_payload(
                recipientEmail=recipient_email,
                recipientPhone=recipient_phone,
                messageTitle=message_title,
                messageBody=message_body,
            ),
            bearer_token=access_token,
            extra_headers=self._mcp_headers(idempotency_key),
        )

    async def sync_monetization_payment_status(
        self,
        *,
        access_token: str,
        payment_id: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            f"/payments/monetization-payments/{payment_id}/sync-status",
            bearer_token=access_token,
            extra_headers=self._mcp_headers(),
        )
