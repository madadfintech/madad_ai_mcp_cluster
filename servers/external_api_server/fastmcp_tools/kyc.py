from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from tools.api_wrappers.read.non_transactional import MadadKYCNonTransactionalReadAPI
from tools.api_wrappers.write.transactional import MadadKYCTransactionalWriteAPI

from . import mcp


kyc_write_api = MadadKYCTransactionalWriteAPI()
kyc_read_api = MadadKYCNonTransactionalReadAPI()


class ShareholderAddressInput(BaseModel):
    zone: Optional[str] = None
    streetNo: Optional[str] = None
    buildingNo: Optional[str] = None
    floorNo: Optional[str] = None
    unitNo: Optional[str] = None


class ShareholderInput(BaseModel):
    name: str = Field(description="Full shareholder name. Required by backend validation.")
    phoneNumber: str = Field(description="Shareholder phone number. Use this exact key, not phone.")
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    middleName: Optional[str] = None
    email: Optional[str] = None
    address: Optional[ShareholderAddressInput] = None


@mcp.tool
async def madad_kyc_update_eligibility(
    access_token: str,
    is_qatar_based: bool,
    business_age: str,
    cr_validity: str,
    company_type: str,
    sector: str,
    turnover: str,
    employees: str,
) -> Dict[str, Any]:
    """Update the merchant eligibility answers for the KYC journey."""
    return await kyc_write_api.update_eligibility(
        access_token=access_token,
        is_qatar_based=is_qatar_based,
        business_age=business_age,
        cr_validity=cr_validity,
        company_type=company_type,
        sector=sector,
        turnover=turnover,
        employees=employees,
    )


@mcp.tool
async def madad_kyc_upload_document(
    file_path: str,
    document_entity_type: str,
    document_type: str,
    access_token: str,
    kyc_stage: Optional[str] = None,
    document_param: Optional[str] = None,
    document_label: Optional[str] = None,
    from_admin: bool = False,
    target_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload a KYC document from a trusted local worker file path to Madad."""
    return await kyc_write_api.upload_document(
        file_path=file_path,
        document_entity_type=document_entity_type,
        document_type=document_type,
        access_token=access_token,
        kyc_stage=kyc_stage,
        document_param=document_param,
        document_label=document_label,
        from_admin=from_admin,
        target_user_id=target_user_id,
    )


@mcp.tool
async def madad_kyc_upload_document_base64(
    file_name: str,
    mime_type: str,
    base64: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Upload a KYC document from base64 bytes received from WhatsApp or email.

    Metadata keys: access_token, document_entity_type, document_type, kyc_stage,
    document_param, document_label, from_admin, target_user_id.
    """
    access_token = metadata.get("access_token")
    document_entity_type = metadata.get("document_entity_type") or metadata.get("documentEntityType")
    document_type = metadata.get("document_type") or metadata.get("documentType")

    if not access_token:
        raise ValueError("metadata.access_token is required")
    if not document_entity_type:
        raise ValueError("metadata.document_entity_type is required")
    if not document_type:
        raise ValueError("metadata.document_type is required")

    return await kyc_write_api.upload_document_base64(
        file_name=file_name,
        file_base64=base64,
        document_entity_type=document_entity_type,
        document_type=document_type,
        access_token=access_token,
        mime_type=mime_type,
        kyc_stage=metadata.get("kyc_stage") or metadata.get("kycStage"),
        document_param=metadata.get("document_param") or metadata.get("documentParam"),
        document_label=metadata.get("document_label") or metadata.get("documentLabel"),
        from_admin=metadata.get("from_admin", metadata.get("fromAdmin", False)),
        target_user_id=metadata.get("target_user_id") or metadata.get("targetUserId"),
    )


@mcp.tool
async def madad_kyc_upload_commercial_registration(
    file_path: str,
    access_token: str,
    document_label: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload a Commercial Registration document for the merchant."""
    return await kyc_write_api.upload_commercial_registration(
        file_path=file_path,
        access_token=access_token,
        document_label=document_label,
    )


@mcp.tool
async def madad_kyc_upload_audited_financial_report(
    file_path: str,
    access_token: str,
    document_param: Optional[str] = None,
    document_label: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload an audited financial report for the merchant."""
    return await kyc_write_api.upload_audited_financial_report(
        file_path=file_path,
        access_token=access_token,
        document_param=document_param,
        document_label=document_label,
    )


@mcp.tool
def madad_kyc_inspect_zip(zip_path: str) -> Dict[str, Any]:
    """List uploadable files inside a ZIP before mapping them to document types."""
    return kyc_write_api.inspect_zip_documents(zip_path=zip_path)


@mcp.tool
async def madad_kyc_upload_zip_documents(
    zip_path: str,
    access_token: str,
    documents: List[Dict[str, Any]],
    continue_on_error: bool = True,
) -> Dict[str, Any]:
    """Extract a ZIP and upload explicitly mapped documents one by one."""
    return await kyc_write_api.upload_zip_documents(
        zip_path=zip_path,
        access_token=access_token,
        documents=documents,
        continue_on_error=continue_on_error,
    )


@mcp.tool
async def madad_kyc_get_documents(access_token: str) -> Dict[str, Any]:
    """Get all KYC documents uploaded by the current user."""
    return await kyc_read_api.get_documents(access_token=access_token)


@mcp.tool
async def madad_kyc_get_business_documents(access_token: str) -> Dict[str, Any]:
    """Get business documents uploaded by the current user."""
    return await kyc_read_api.get_business_documents(access_token=access_token)


@mcp.tool
async def madad_kyc_get_financial_documents(access_token: str) -> Dict[str, Any]:
    """Get financial documents uploaded by the current user."""
    return await kyc_read_api.get_financial_documents(access_token=access_token)


@mcp.tool
async def madad_kyc_get_admin_requested_documents(access_token: str) -> Dict[str, Any]:
    """Get documents requested by admin for the current user."""
    return await kyc_read_api.get_admin_requested_documents(access_token=access_token)


@mcp.tool
async def madad_kyc_get_business_details(access_token: str) -> Dict[str, Any]:
    """Get the current user's business details record."""
    return await kyc_read_api.get_business_details(access_token=access_token)


@mcp.tool
async def madad_kyc_delete_document(access_token: str, document_id: str) -> Dict[str, Any]:
    """Soft-delete an uploaded KYC document."""
    return await kyc_write_api.delete_document(access_token=access_token, document_id=document_id)


@mcp.tool
async def madad_kyc_update_business_details(
    access_token: str,
    legal_entity_name: Optional[str] = None,
    cr_number: Optional[str] = None,
    legal_form: Optional[str] = None,
    cr_issue_date: Optional[str] = None,
    cr_expiry_date: Optional[str] = None,
    tax_reg_no: Optional[str] = None,
    tin_number: Optional[str] = None,
    business_city: Optional[str] = None,
    business_country: Optional[str] = None,
) -> Dict[str, Any]:
    """Update merchant business registration details."""
    return await kyc_write_api.update_business_details(
        access_token=access_token,
        legal_entity_name=legal_entity_name,
        cr_number=cr_number,
        legal_form=legal_form,
        cr_issue_date=cr_issue_date,
        cr_expiry_date=cr_expiry_date,
        tax_reg_no=tax_reg_no,
        tin_number=tin_number,
        business_city=business_city,
        business_country=business_country,
    )


@mcp.tool
async def madad_kyc_update_primary_details(
    access_token: str,
    first_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    last_name: Optional[str] = None,
    qid_number: Optional[str] = None,
    qid_expiry_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Update primary applicant details for the merchant application."""
    return await kyc_write_api.update_primary_details(
        access_token=access_token,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        qid_number=qid_number,
        qid_expiry_date=qid_expiry_date,
    )


@mcp.tool
async def madad_kyc_update_sector_detail(
    access_token: str,
    sector: str,
    sub_sector: str,
) -> Dict[str, Any]:
    """Update the merchant sector and sub-sector details."""
    return await kyc_write_api.update_sector_detail(
        access_token=access_token,
        sector=sector,
        sub_sector=sub_sector,
    )


@mcp.tool
async def madad_kyc_complete_stage(access_token: str, stage: str) -> Dict[str, Any]:
    """Mark a KYC stage as complete."""
    return await kyc_write_api.complete_stage(access_token=access_token, stage=stage)


@mcp.tool
async def madad_kyc_add_shareholders(
    access_token: str,
    shareholders: List[ShareholderInput],
) -> Dict[str, Any]:
    """Add one or more shareholders to the merchant application.

    Required per shareholder: name and phoneNumber. The backend derives the
    user/business from the bearer token; businessDetailsId is not accepted here.
    Ownership percentage, nationality, and identity document fields are not part
    of this endpoint. Upload shareholder documents separately after creation.
    """
    payload = [shareholder.model_dump(exclude_none=True) for shareholder in shareholders]
    return await kyc_write_api.add_shareholders(access_token=access_token, shareholders=payload)


@mcp.tool
async def madad_kyc_get_shareholders(access_token: str) -> Dict[str, Any]:
    """List shareholders for the current merchant."""
    return await kyc_read_api.get_shareholders(access_token=access_token)


@mcp.tool
async def madad_kyc_get_shareholders_kyc_status(access_token: str) -> Dict[str, Any]:
    """Get KYC verification status for all shareholders."""
    return await kyc_read_api.get_shareholders_kyc_status(access_token=access_token)


@mcp.tool
async def madad_kyc_get_shareholders_consents(access_token: str) -> Dict[str, Any]:
    """Get individual consent records for all shareholders."""
    return await kyc_read_api.get_shareholders_consents(access_token=access_token)


@mcp.tool
async def madad_kyc_update_shareholder(
    access_token: str,
    shareholder_id: str,
    first_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing shareholder."""
    return await kyc_write_api.update_shareholder(
        access_token=access_token,
        shareholder_id=shareholder_id,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
    )


@mcp.tool
async def madad_kyc_delete_shareholder(access_token: str, shareholder_id: str) -> Dict[str, Any]:
    """Delete a shareholder from the merchant application."""
    return await kyc_write_api.delete_shareholder(access_token=access_token, shareholder_id=shareholder_id)


@mcp.tool
async def madad_kyc_upload_shareholder_documents(
    access_token: str,
    shareholder_id: str,
    files: Dict[str, str],
) -> Dict[str, Any]:
    """Upload documents for an existing shareholder. The files map is DocumentType to local path."""
    return await kyc_write_api.upload_shareholder_documents(
        access_token=access_token,
        shareholder_id=shareholder_id,
        files=files,
    )


@mcp.tool
async def madad_kyc_add_buyer(
    access_token: str,
    name: str,
    cr_number: Optional[str] = None,
    contact_person: Optional[str] = None,
    contact_number: Optional[str] = None,
    contact_email: Optional[str] = None,
    buyer_type: Optional[str] = None,
    buyer_sector: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a buyer/paymaster to the merchant's buyer list."""
    return await kyc_write_api.add_buyer(
        access_token=access_token,
        name=name,
        cr_number=cr_number,
        contact_person=contact_person,
        contact_number=contact_number,
        contact_email=contact_email,
        buyer_type=buyer_type,
        buyer_sector=buyer_sector,
    )


@mcp.tool
async def madad_kyc_get_buyers(access_token: str) -> Dict[str, Any]:
    """List buyers/paymasters for the current merchant."""
    return await kyc_read_api.get_buyers(access_token=access_token)


@mcp.tool
async def madad_kyc_get_primary_bank_detail(access_token: str) -> Dict[str, Any]:
    """Get primary bank detail for the current merchant."""
    return await kyc_read_api.get_primary_bank_detail(access_token=access_token)


@mcp.tool
async def madad_kyc_edit_buyer(
    access_token: str,
    buyer_id: str,
    name: Optional[str] = None,
    cr_number: Optional[str] = None,
    contact_person: Optional[str] = None,
    contact_number: Optional[str] = None,
    contact_email: Optional[str] = None,
    buyer_type: Optional[str] = None,
    buyer_sector: Optional[str] = None,
) -> Dict[str, Any]:
    """Edit a buyer/paymaster record."""
    return await kyc_write_api.edit_buyer(
        access_token=access_token,
        buyer_id=buyer_id,
        name=name,
        cr_number=cr_number,
        contact_person=contact_person,
        contact_number=contact_number,
        contact_email=contact_email,
        buyer_type=buyer_type,
        buyer_sector=buyer_sector,
    )


@mcp.tool
async def madad_kyc_delete_buyer(access_token: str, buyer_id: str) -> Dict[str, Any]:
    """Delete a buyer/paymaster record."""
    return await kyc_write_api.delete_buyer(access_token=access_token, buyer_id=buyer_id)
