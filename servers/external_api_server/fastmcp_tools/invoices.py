from typing import Any, Dict, List, Optional

from tools.api_wrappers.read.non_transactional import MadadInvoicesNonTransactionalReadAPI
from tools.api_wrappers.write.transactional import MadadInvoicesTransactionalWriteAPI

from . import mcp


invoices_read_api = MadadInvoicesNonTransactionalReadAPI()
invoices_write_api = MadadInvoicesTransactionalWriteAPI()


@mcp.tool
async def madad_invoices_get_my_invoices(access_token: str) -> Dict[str, Any]:
    """Get invoices uploaded by the current MSME user."""
    return await invoices_read_api.get_my_invoices(access_token=access_token)


@mcp.tool
async def madad_invoices_extract_invoice(
    access_token: str,
    file_path: str,
) -> Dict[str, Any]:
    """Upload an invoice file in extraction-only mode, matching the MSME portal first step."""
    return await invoices_write_api.extract_invoice(
        access_token=access_token,
        file_path=file_path,
    )


@mcp.tool
async def madad_invoices_extract_invoice_base64(
    access_token: str,
    file_name: str,
    file_base64: str,
    mime_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract invoice data from WhatsApp/email attachment bytes."""
    return await invoices_write_api.extract_invoice_base64(
        access_token=access_token,
        file_name=file_name,
        file_base64=file_base64,
        mime_type=mime_type,
    )


@mcp.tool
async def madad_invoices_submit_invoice(
    access_token: str,
    file_path: str,
    user_id: Optional[str] = None,
    status: Optional[str] = "UNVERIFIED",
    is_eligible: Optional[bool] = None,
    invoice_number: Optional[str] = None,
    invoice_date: Optional[str] = None,
    due_date: Optional[str] = None,
    total_amount: Optional[str] = None,
    supplier_name: Optional[str] = None,
    customer_name: Optional[str] = None,
    billing_address: Optional[str] = None,
    customer_address: Optional[str] = None,
    line_items: Optional[List[Dict[str, Any]]] = None,
    is_batch_upload: Optional[bool] = None,
    is_last_in_batch: Optional[bool] = None,
    total_in_batch: Optional[int] = None,
) -> Dict[str, Any]:
    """Submit the final invoice upload using fields extracted by the portal/backend flow."""
    return await invoices_write_api.upload_invoice(
        access_token=access_token,
        file_path=file_path,
        user_id=user_id,
        status=status,
        is_eligible=is_eligible,
        extraction_only=False,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        total_amount=total_amount,
        supplier_name=supplier_name,
        customer_name=customer_name,
        billing_address=billing_address,
        customer_address=customer_address,
        line_items=line_items,
        is_batch_upload=is_batch_upload,
        is_last_in_batch=is_last_in_batch,
        total_in_batch=total_in_batch,
    )


@mcp.tool
async def madad_invoices_submit_invoice_base64(
    access_token: str,
    file_name: str,
    file_base64: str,
    mime_type: Optional[str] = None,
    user_id: Optional[str] = None,
    status: Optional[str] = "UNVERIFIED",
    is_eligible: Optional[bool] = None,
    invoice_number: Optional[str] = None,
    invoice_date: Optional[str] = None,
    due_date: Optional[str] = None,
    total_amount: Optional[str] = None,
    supplier_name: Optional[str] = None,
    customer_name: Optional[str] = None,
    billing_address: Optional[str] = None,
    customer_address: Optional[str] = None,
    line_items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Submit final invoice upload from WhatsApp/email attachment bytes."""
    return await invoices_write_api.upload_invoice_base64(
        access_token=access_token,
        file_name=file_name,
        file_base64=file_base64,
        mime_type=mime_type,
        user_id=user_id,
        status=status,
        is_eligible=is_eligible,
        extraction_only=False,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        total_amount=total_amount,
        supplier_name=supplier_name,
        customer_name=customer_name,
        billing_address=billing_address,
        customer_address=customer_address,
        line_items=line_items,
    )


@mcp.tool
async def madad_invoices_extract_and_submit_invoice(
    access_token: str,
    file_path: str,
    user_id: Optional[str] = None,
    status: str = "UNVERIFIED",
) -> Dict[str, Any]:
    """Extract invoice data, assume it is correct, and submit the invoice."""
    return await invoices_write_api.extract_and_submit_invoice(
        access_token=access_token,
        file_path=file_path,
        user_id=user_id,
        status=status,
    )


@mcp.tool
async def madad_invoices_extract_and_submit_invoice_base64(
    access_token: str,
    file_name: str,
    file_base64: str,
    mime_type: Optional[str] = None,
    user_id: Optional[str] = None,
    status: str = "UNVERIFIED",
) -> Dict[str, Any]:
    """Extract invoice data from bytes, assume it is correct, and submit the invoice."""
    return await invoices_write_api.extract_and_submit_invoice_base64(
        access_token=access_token,
        file_name=file_name,
        file_base64=file_base64,
        mime_type=mime_type,
        user_id=user_id,
        status=status,
    )


@mcp.tool
async def madad_invoices_inspect_zip(zip_path: str) -> Dict[str, Any]:
    """List uploadable invoice files inside a ZIP before recursive upload."""
    return invoices_write_api.inspect_zip_invoices(zip_path=zip_path)


@mcp.tool
async def madad_invoices_upload_zip(
    access_token: str,
    zip_path: str,
    user_id: Optional[str] = None,
    status: str = "UNVERIFIED",
    assume_extracted_data_correct: bool = True,
    continue_on_error: bool = True,
) -> Dict[str, Any]:
    """Extract a ZIP and upload each invoice through the MSME invoice upload flow."""
    return await invoices_write_api.upload_zip_invoices(
        access_token=access_token,
        zip_path=zip_path,
        user_id=user_id,
        status=status,
        assume_extracted_data_correct=assume_extracted_data_correct,
        continue_on_error=continue_on_error,
    )
