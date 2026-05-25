from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional
from zipfile import BadZipFile, ZipFile

from tools.api_wrappers.common import MadadAPIClient
from tools.api_wrappers.madad_client import MadadAPIError


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
        document_label: Optional[str] = None,
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
                documentLabel=document_label,
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
        document_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.upload_document(
            file_path=file_path,
            document_entity_type=document_entity_type,
            document_type=document_type,
            access_token=access_token,
            kyc_stage=kyc_stage,
            document_param=document_param,
            document_label=document_label,
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
        document_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.upload_document(
            file_path=file_path,
            document_entity_type=document_entity_type,
            document_type=document_type,
            access_token=access_token,
            kyc_stage=kyc_stage,
            document_param=document_param,
            document_label=document_label,
            from_admin=False,
        )

    async def delete_document(self, *, access_token: str, document_id: str) -> Dict[str, Any]:
        return await self.client.request(
            "DELETE",
            f"/kyc/document/{document_id}",
            bearer_token=access_token,
        )

    async def update_business_details(
        self,
        *,
        access_token: str,
        legal_entity_name: Optional[str] = None,
        cr_number: Optional[str] = None,
        legal_form: Optional[str] = None,
        cr_issue_date: Optional[str] = None,
        cr_expiry_date: Optional[str] = None,
        tax_reg_no: Optional[str] = None,
        tin_number: Optional[str] = None,
        branch_count: Optional[int] = None,
        firm_nationality: Optional[str] = None,
        establishment_id: Optional[str] = None,
        establishment_id_issue_date: Optional[str] = None,
        establishment_id_expiry_date: Optional[str] = None,
        establishment_name: Optional[str] = None,
        tl_issue_date: Optional[str] = None,
        tl_expiry_date: Optional[str] = None,
        ownership_type: Optional[str] = None,
        tl_number: Optional[str] = None,
        business_address_line_1: Optional[str] = None,
        business_address_line_2: Optional[str] = None,
        business_city: Optional[str] = None,
        business_country: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/kyc/update-business-details",
            json_body=compact_payload(
                legalEntityName=legal_entity_name,
                crNumber=cr_number,
                legalForm=legal_form,
                crIssueDate=cr_issue_date,
                crExpiryDate=cr_expiry_date,
                taxRegNo=tax_reg_no,
                tinNumber=tin_number,
                branchCount=branch_count,
                firmNationality=firm_nationality,
                establishmentId=establishment_id,
                establishmentIdIssueDate=establishment_id_issue_date,
                establishmentIdExpiryDate=establishment_id_expiry_date,
                establishmentName=establishment_name,
                tlIssueDate=tl_issue_date,
                tlExpiryDate=tl_expiry_date,
                ownershipType=ownership_type,
                tlNumber=tl_number,
                businessAddressLine1=business_address_line_1,
                businessAddressLine2=business_address_line_2,
                businessCity=business_city,
                businessCountry=business_country,
            ),
            bearer_token=access_token,
        )

    async def update_primary_details(
        self,
        *,
        access_token: str,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        qid_number: Optional[str] = None,
        qid_expiry_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/kyc/update-primary-details",
            json_body=compact_payload(
                firstName=first_name,
                middleName=middle_name,
                lastName=last_name,
                qidNumber=qid_number,
                qidExpiryDate=qid_expiry_date,
            ),
            bearer_token=access_token,
        )

    async def update_sector_detail(
        self,
        *,
        access_token: str,
        sector: str,
        sub_sector: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "PUT",
            "/kyc/sector-detail",
            json_body={"sector": sector, "subSector": sub_sector},
            bearer_token=access_token,
        )

    async def complete_stage(self, *, access_token: str, stage: str) -> Dict[str, Any]:
        return await self.client.request(
            "PUT",
            f"/kyc/complete-stage/{stage}",
            bearer_token=access_token,
        )

    async def add_shareholders(
        self,
        *,
        access_token: str,
        shareholders: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/kyc/add-shareholder",
            json_body={"shareholders": shareholders},
            bearer_token=access_token,
        )

    async def update_shareholder(
        self,
        *,
        access_token: str,
        shareholder_id: str,
        first_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "PATCH",
            f"/kyc/shareholder/{shareholder_id}",
            json_body=compact_payload(
                firstName=first_name,
                middleName=middle_name,
                lastName=last_name,
                email=email,
                phoneNumber=phone_number,
            ),
            bearer_token=access_token,
        )

    async def delete_shareholder(self, *, access_token: str, shareholder_id: str) -> Dict[str, Any]:
        return await self.client.request(
            "DELETE",
            f"/kyc/shareholder/{shareholder_id}",
            bearer_token=access_token,
        )

    async def upload_shareholder_documents(
        self,
        *,
        access_token: str,
        shareholder_id: str,
        files: Dict[str, str],
    ) -> Dict[str, Any]:
        return await self.client.upload_files(
            f"/kyc/upload-shareholder-documents/{shareholder_id}",
            file_fields=files,
            bearer_token=access_token,
        )

    async def add_buyer(
        self,
        *,
        access_token: str,
        name: str,
        cr_number: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_number: Optional[str] = None,
        contact_email: Optional[str] = None,
        buyer_type: Optional[str] = None,
        buyer_sector: Optional[str] = None,
        logo_url: Optional[str] = None,
        poc_designation: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        form_data = compact_payload(
            name=name,
            crNumber=cr_number,
            contactPerson=contact_person,
            contactNumber=contact_number,
            contactEmail=contact_email,
            buyerType=buyer_type,
            buyerSector=buyer_sector,
            logoUrl=logo_url,
            pocDesignation=poc_designation,
        )
        if logo_path:
            return await self.client.upload_files(
                "/kyc/add-buyer",
                file_fields={"logo": logo_path},
                form_data=form_data,
                bearer_token=access_token,
            )

        return await self.client.request(
            "POST",
            "/kyc/add-buyer",
            json_body=form_data,
            bearer_token=access_token,
        )

    async def edit_buyer(
        self,
        *,
        access_token: str,
        buyer_id: str,
        name: Optional[str] = None,
        cr_number: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_number: Optional[str] = None,
        contact_email: Optional[str] = None,
        buyer_type: Optional[str] = None,
        buyer_sector: Optional[str] = None,
        logo_url: Optional[str] = None,
        poc_designation: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        form_data = compact_payload(
            buyerId=buyer_id,
            name=name,
            crNumber=cr_number,
            contactPerson=contact_person,
            contactNumber=contact_number,
            contactEmail=contact_email,
            buyerType=buyer_type,
            buyerSector=buyer_sector,
            logoUrl=logo_url,
            pocDesignation=poc_designation,
        )
        if logo_path:
            return await self.client.upload_files(
                "/kyc/edit-buyer",
                file_fields={"logo": logo_path},
                form_data=form_data,
                bearer_token=access_token,
            )

        return await self.client.request(
            "PUT",
            "/kyc/edit-buyer",
            json_body=form_data,
            bearer_token=access_token,
        )

    async def delete_buyer(self, *, access_token: str, buyer_id: str) -> Dict[str, Any]:
        return await self.client.request(
            "DELETE",
            f"/kyc/buyer/{buyer_id}",
            bearer_token=access_token,
        )

    def inspect_zip_documents(self, *, zip_path: str) -> Dict[str, Any]:
        local_path = Path(zip_path).expanduser()
        if not local_path.is_file():
            raise MadadAPIError(f"File not found: {zip_path}")

        try:
            with ZipFile(local_path) as archive:
                entries = [
                    {
                        "archive_path": info.filename,
                        "file_name": Path(info.filename).name,
                        "size": info.file_size,
                    }
                    for info in archive.infolist()
                    if self._is_uploadable_zip_member(info.filename)
                ]
        except BadZipFile as exc:
            raise MadadAPIError(f"Invalid zip file: {zip_path}") from exc

        return {"zip_path": str(local_path), "total_files": len(entries), "files": entries}

    async def upload_zip_documents(
        self,
        *,
        zip_path: str,
        access_token: str,
        documents: List[Dict[str, Any]],
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        local_path = Path(zip_path).expanduser()
        if not local_path.is_file():
            raise MadadAPIError(f"File not found: {zip_path}")

        upload_plan = {item["archive_path"]: item for item in documents}
        uploaded: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []

        try:
            with TemporaryDirectory(prefix="madad_kyc_zip_") as temp_dir:
                temp_root = Path(temp_dir).resolve()
                with ZipFile(local_path) as archive:
                    for info in archive.infolist():
                        if not self._is_uploadable_zip_member(info.filename):
                            continue

                        plan = upload_plan.get(info.filename)
                        if not plan:
                            skipped.append(
                                {
                                    "archive_path": info.filename,
                                    "reason": "No upload mapping supplied for this file.",
                                }
                            )
                            continue

                        extracted_path = self._safe_extract_member(archive, info.filename, temp_root)
                        try:
                            response = await self.upload_document(
                                file_path=str(extracted_path),
                                document_entity_type=plan["document_entity_type"],
                                document_type=plan["document_type"],
                                access_token=access_token,
                                kyc_stage=plan.get("kyc_stage"),
                                document_param=plan.get("document_param"),
                                document_label=plan.get("document_label"),
                                from_admin=plan.get("from_admin"),
                                target_user_id=plan.get("target_user_id"),
                            )
                            uploaded.append(
                                {
                                    "archive_path": info.filename,
                                    "file_name": extracted_path.name,
                                    "response": response,
                                }
                            )
                        except Exception as exc:
                            errors.append({"archive_path": info.filename, "error": str(exc)})
                            if not continue_on_error:
                                raise
        except BadZipFile as exc:
            raise MadadAPIError(f"Invalid zip file: {zip_path}") from exc

        return {
            "success": not errors,
            "zip_path": str(local_path),
            "uploaded_count": len(uploaded),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "uploaded": uploaded,
            "skipped": skipped,
            "errors": errors,
        }

    @staticmethod
    def _is_uploadable_zip_member(name: str) -> bool:
        path = Path(name)
        if name.endswith("/") or not path.name:
            return False
        if path.name.startswith(".") or "__MACOSX" in path.parts:
            return False
        return True

    @staticmethod
    def _safe_extract_member(archive: ZipFile, member_name: str, temp_root: Path) -> Path:
        destination = (temp_root / member_name).resolve()
        if not destination.is_relative_to(temp_root):
            raise MadadAPIError(f"Unsafe zip member path: {member_name}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(member_name) as source, destination.open("wb") as target:
            target.write(source.read())
        return destination
