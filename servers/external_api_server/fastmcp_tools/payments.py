from typing import Any, Dict, List, Optional

from tools.api_wrappers.read.non_transactional import MadadPaymentsNonTransactionalReadAPI
from tools.api_wrappers.write.transactional import MadadPaymentsTransactionalWriteAPI

from . import mcp


payments_read_api = MadadPaymentsNonTransactionalReadAPI()
payments_write_api = MadadPaymentsTransactionalWriteAPI()


@mcp.tool
async def madad_payments_list_monetization_products(
    access_token: str,
    search: Optional[str] = None,
    status: Optional[str] = "ACTIVE",
) -> Dict[str, Any]:
    """List monetization products such as the onboarding and assessment fee."""
    return await payments_read_api.list_monetization_products(
        access_token=access_token,
        search=search,
        status=status,
    )


@mcp.tool
async def madad_payments_create_monetization_payment(
    access_token: str,
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
    """Create a recorded TESS monetization payment and checkout link."""
    return await payments_write_api.create_monetization_payment(
        access_token=access_token,
        business_details_id=business_details_id,
        product_id=product_id,
        payable_amount=payable_amount,
        mode_of_payment=mode_of_payment,
        operation=operation,
        methods=methods,
        session_expiry_minutes=session_expiry_minutes,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
        custom_data=custom_data,
    )


@mcp.tool
async def madad_payments_send_monetization_payment_link(
    access_token: str,
    payment_id: str,
    recipient_email: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    message_title: Optional[str] = None,
    message_body: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an existing monetization payment link by backend email or SMS."""
    return await payments_write_api.send_monetization_payment_link(
        access_token=access_token,
        payment_id=payment_id,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
        message_title=message_title,
        message_body=message_body,
    )


@mcp.tool
async def madad_payments_get_monetization_payment(
    access_token: str,
    payment_id: str,
) -> Dict[str, Any]:
    """Get a TESS monetization payment record by id."""
    return await payments_read_api.get_monetization_payment(
        access_token=access_token,
        payment_id=payment_id,
    )


@mcp.tool
async def madad_payments_sync_monetization_payment_status(
    access_token: str,
    payment_id: str,
) -> Dict[str, Any]:
    """Refresh a payment status from TESS and update the backend record."""
    return await payments_write_api.sync_monetization_payment_status(
        access_token=access_token,
        payment_id=payment_id,
    )


