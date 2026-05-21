from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


def compact_payload(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


class MadadKYCTransactionalWriteAPI:
    """Write-capable Madad KYC endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def update_eligibility(
        self,
        *,
        access_token: str,
        is_qatar_based: bool,
        business_age: str,
        cr_validity: str,
        company_type: str,
        sector: str,
        turnover: str,
        employees: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "PATCH",
            "/kyc/eligibility",
            json_body={
                "kyc": {
                    "businessDetails": {
                        "isQatarBased": is_qatar_based,
                        "businessAge": business_age,
                        "crValidity": cr_validity,
                        "companyType": company_type,
                        "sector": sector,
                        "turnover": turnover,
                        "employees": employees,
                    }
                }
            },
            bearer_token=access_token,
        )

    async def upload_document(
        self,
        *,
        file_path: str,
        document_entity_type: str,
        document_type: str,
        access_token: str,
        kyc_stage: Optional[str] = None,
        document_param: Optional[str] = None,
        from_admin: Optional[bool] = None,
        target_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if from_admin is not None:
            params["fromAdmin"] = str(from_admin).lower()
        if target_user_id:
            params["targetUserId"] = target_user_id

        return await self.client.upload_file(
            "/kyc/upload-document",
            file_path=file_path,
            form_data=compact_payload(
                documentEntityType=document_entity_type,
                documentType=document_type,
                kycStage=kyc_stage,
                documentParam=document_param,
            ),
            params=params or None,
            bearer_token=access_token,
        )

    async def upload_commercial_registration(
        self,
        *,
        file_path: str,
        access_token: str,
        document_entity_type: str = "BUSINESS_DETAILS",
        document_type: str = "COMMERCIAL_REGISTRATION",
        kyc_stage: str = "Business Documents",
        document_param: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.upload_document(
            file_path=file_path,
            document_entity_type=document_entity_type,
            document_type=document_type,
            access_token=access_token,
            kyc_stage=kyc_stage,
            document_param=document_param,
            from_admin=False,
        )

    async def upload_audited_financial_report(
        self,
        *,
        file_path: str,
        access_token: str,
        document_entity_type: str = "BUSINESS_DETAILS",
        document_type: str = "AUDITED_FINANCIAL_REPORT",
        kyc_stage: str = "Financial Documents",
        document_param: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.upload_document(
            file_path=file_path,
            document_entity_type=document_entity_type,
            document_type=document_type,
            access_token=access_token,
            kyc_stage=kyc_stage,
            document_param=document_param,
            from_admin=False,
        )
