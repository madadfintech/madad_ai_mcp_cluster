import base64
import binascii
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional
from zipfile import BadZipFile, ZipFile

from tools.api_wrappers.common import MadadAPIClient
from tools.api_wrappers.madad_client import MadadAPIError


def compact_payload(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


class MadadInvoicesTransactionalWriteAPI:
    """Write-capable Madad invoice endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def extract_invoice(
        self,
        *,
        access_token: str,
        file_path: str,
    ) -> Dict[str, Any]:
        return await self.upload_invoice(
            access_token=access_token,
            file_path=file_path,
            extraction_only=True,
        )

    async def extract_invoice_base64(
        self,
        *,
        access_token: str,
        file_name: str,
        file_base64: str,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.upload_invoice_base64(
            access_token=access_token,
            file_name=file_name,
            file_base64=file_base64,
            mime_type=mime_type,
            extraction_only=True,
        )

    async def upload_invoice(
        self,
        *,
        access_token: str,
        file_path: str,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_eligible: Optional[bool] = None,
        extraction_only: bool = False,
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
        return await self.client.upload_file(
            "/invoices/upload",
            file_path=file_path,
            form_data=self._invoice_form_data(
                user_id=user_id,
                status=status,
                is_eligible=is_eligible,
                extraction_only=extraction_only,
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
            ),
            bearer_token=access_token,
        )

    async def upload_invoice_base64(
        self,
        *,
        access_token: str,
        file_name: str,
        file_base64: str,
        mime_type: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        is_eligible: Optional[bool] = None,
        extraction_only: bool = False,
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
        file_bytes = self._decode_base64_file(file_base64)
        return await self.client.upload_file_bytes(
            "/invoices/upload",
            file_name=file_name,
            file_bytes=file_bytes,
            content_type=mime_type,
            form_data=self._invoice_form_data(
                user_id=user_id,
                status=status,
                is_eligible=is_eligible,
                extraction_only=extraction_only,
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
            ),
            bearer_token=access_token,
        )

    async def extract_and_submit_invoice(
        self,
        *,
        access_token: str,
        file_path: str,
        user_id: Optional[str] = None,
        status: str = "UNVERIFIED",
    ) -> Dict[str, Any]:
        extraction = await self.extract_invoice(
            access_token=access_token,
            file_path=file_path,
        )
        mapped = self._map_extracted_invoice_data(extraction)
        submission = await self.upload_invoice(
            access_token=access_token,
            file_path=file_path,
            user_id=user_id,
            status=status,
            extraction_only=False,
            invoice_number=mapped.get("invoiceNumber"),
            invoice_date=mapped.get("invoiceDate"),
            due_date=mapped.get("dueDate"),
            total_amount=mapped.get("totalAmount"),
            supplier_name=mapped.get("supplierName"),
            customer_name=mapped.get("customerName"),
            line_items=mapped.get("lineItems"),
        )
        return {
            "success": not submission.get("body", {}).get("success") is False,
            "extraction": extraction,
            "mapped_extracted_data": mapped,
            "submission": submission,
        }

    async def extract_and_submit_invoice_base64(
        self,
        *,
        access_token: str,
        file_name: str,
        file_base64: str,
        mime_type: Optional[str] = None,
        user_id: Optional[str] = None,
        status: str = "UNVERIFIED",
    ) -> Dict[str, Any]:
        extraction = await self.extract_invoice_base64(
            access_token=access_token,
            file_name=file_name,
            file_base64=file_base64,
            mime_type=mime_type,
        )
        mapped = self._map_extracted_invoice_data(extraction)
        submission = await self.upload_invoice_base64(
            access_token=access_token,
            file_name=file_name,
            file_base64=file_base64,
            mime_type=mime_type,
            user_id=user_id,
            status=status,
            extraction_only=False,
            invoice_number=mapped.get("invoiceNumber"),
            invoice_date=mapped.get("invoiceDate"),
            due_date=mapped.get("dueDate"),
            total_amount=mapped.get("totalAmount"),
            supplier_name=mapped.get("supplierName"),
            customer_name=mapped.get("customerName"),
            line_items=mapped.get("lineItems"),
        )
        return {
            "success": not submission.get("body", {}).get("success") is False,
            "extraction": extraction,
            "mapped_extracted_data": mapped,
            "submission": submission,
        }

    def inspect_zip_invoices(self, *, zip_path: str) -> Dict[str, Any]:
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

    async def upload_zip_invoices(
        self,
        *,
        access_token: str,
        zip_path: str,
        user_id: Optional[str] = None,
        status: str = "UNVERIFIED",
        assume_extracted_data_correct: bool = True,
        continue_on_error: bool = True,
    ) -> Dict[str, Any]:
        local_path = Path(zip_path).expanduser()
        if not local_path.is_file():
            raise MadadAPIError(f"File not found: {zip_path}")

        uploaded: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []

        try:
            with TemporaryDirectory(prefix="madad_invoice_zip_") as temp_dir:
                temp_root = Path(temp_dir).resolve()
                with ZipFile(local_path) as archive:
                    members = [
                        info
                        for info in archive.infolist()
                        if self._is_uploadable_zip_member(info.filename)
                    ]
                    total = len(members)

                    for index, info in enumerate(members):
                        extracted_path = self._safe_extract_member(archive, info.filename, temp_root)
                        try:
                            if assume_extracted_data_correct:
                                response = await self.extract_and_submit_invoice(
                                    access_token=access_token,
                                    file_path=str(extracted_path),
                                    user_id=user_id,
                                    status=status,
                                )
                            else:
                                response = await self.upload_invoice(
                                    access_token=access_token,
                                    file_path=str(extracted_path),
                                    user_id=user_id,
                                    status=status,
                                    extraction_only=False,
                                    is_batch_upload=True,
                                    is_last_in_batch=index == total - 1,
                                    total_in_batch=total if total > 1 else None,
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
            "error_count": len(errors),
            "uploaded": uploaded,
            "errors": errors,
        }

    def _invoice_form_data(self, **kwargs: Any) -> Dict[str, Any]:
        form_data = compact_payload(**kwargs)
        if "extraction_only" in form_data:
            form_data["extractionOnly"] = str(form_data.pop("extraction_only")).lower()
        if "is_eligible" in form_data:
            form_data["isEligible"] = str(form_data.pop("is_eligible")).lower()
        if "is_batch_upload" in form_data:
            form_data["isBatchUpload"] = str(form_data.pop("is_batch_upload")).lower()
        if "is_last_in_batch" in form_data:
            form_data["isLastInBatch"] = str(form_data.pop("is_last_in_batch")).lower()
        if "total_in_batch" in form_data:
            form_data["totalInBatch"] = form_data.pop("total_in_batch")
        if "invoice_number" in form_data:
            form_data["invoiceNumber"] = form_data.pop("invoice_number")
        if "invoice_date" in form_data:
            form_data["invoiceDate"] = form_data.pop("invoice_date")
        if "due_date" in form_data:
            form_data["dueDate"] = form_data.pop("due_date")
        if "total_amount" in form_data:
            form_data["totalAmount"] = form_data.pop("total_amount")
        if "supplier_name" in form_data:
            form_data["supplierName"] = form_data.pop("supplier_name")
        if "customer_name" in form_data:
            form_data["customerName"] = form_data.pop("customer_name")
        if "billing_address" in form_data:
            form_data["billingAddress"] = form_data.pop("billing_address")
        if "customer_address" in form_data:
            form_data["customerAddress"] = form_data.pop("customer_address")
        if "line_items" in form_data:
            form_data["lineItems"] = json.dumps(form_data.pop("line_items"))
        if "user_id" in form_data:
            form_data["userId"] = form_data.pop("user_id")
        return form_data

    def _map_extracted_invoice_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        data = response.get("body", {}).get("data", {})
        root = data.get("extractedData") or data
        fields = root.get("fields") if isinstance(root, dict) else {}
        if not isinstance(fields, dict):
            fields = root if isinstance(root, dict) else {}

        return {
            "invoiceNumber": fields.get("invoice_number") or fields.get("cr_number") or "",
            "invoiceDate": fields.get("date") or fields.get("invoice_date") or "",
            "dueDate": fields.get("due_date") or "",
            "totalAmount": fields.get("total_amount") or fields.get("amount") or "",
            "currency": fields.get("currency") or "QAR",
            "customerName": (
                fields.get("buyer_name")
                or fields.get("business_name")
                or fields.get("customer_name")
                or ""
            ),
            "customerEmail": fields.get("buyer_email") or fields.get("customer_email") or "",
            "supplierName": fields.get("supplier_name") or fields.get("vendor_name") or "",
            "supplierEmail": fields.get("supplier_email") or fields.get("vendor_email") or "",
            "lineItems": fields.get("line_items") or [],
        }

    @staticmethod
    def _decode_base64_file(file_base64: str) -> bytes:
        try:
            encoded = file_base64.split(",", 1)[1] if "," in file_base64[:128] else file_base64
            return base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise MadadAPIError("Invalid base64 file payload") from exc

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
