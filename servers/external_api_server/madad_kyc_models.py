from typing import Optional

from pydantic import BaseModel, Field


class UpdateEligibilityRequest(BaseModel):
    access_token: str = Field(description="Bearer access token.")
    is_qatar_based: bool = Field(description="Whether the business is Qatar-based.")
    business_age: str = Field(description="Business age, for example OVER_2_YEARS.")
    cr_validity: str = Field(description="CR validity, for example OVER_1_MONTH.")
    company_type: str = Field(description="Company type.")
    sector: str = Field(description="Business sector.")
    turnover: str = Field(description="Annual turnover range.")
    employees: str = Field(description="Number of employees range.")


class UploadKYCDocumentRequest(BaseModel):
    file_path: str = Field(description="Local path to the document file.")
    document_entity_type: str = Field(description="Document entity type.")
    document_type: str = Field(description="Document type.")
    access_token: str = Field(description="Bearer access token.")
    kyc_stage: Optional[str] = Field(default=None, description="KYC stage.")
    document_param: Optional[str] = Field(default=None, description="Additional document parameter.")
    from_admin: Optional[bool] = Field(default=False, description="Upload on behalf of a user.")
    target_user_id: Optional[str] = Field(default=None, description="Target user ID for admin uploads.")


class UploadCommercialRegistrationRequest(BaseModel):
    file_path: str = Field(description="Local path to the CR document.")
    access_token: str = Field(description="Bearer access token.")
    document_entity_type: str = "BUSINESS_DETAILS"
    document_type: str = "COMMERCIAL_REGISTRATION"
    kyc_stage: str = "Business Documents"
    document_param: Optional[str] = None


class UploadAuditedFinancialReportRequest(BaseModel):
    file_path: str = Field(description="Local path to the audited financial report.")
    access_token: str = Field(description="Bearer access token.")
    document_entity_type: str = "BUSINESS_DETAILS"
    document_type: str = "AUDITED_FINANCIAL_REPORT"
    kyc_stage: str = "Financial Documents"
    document_param: Optional[str] = None
