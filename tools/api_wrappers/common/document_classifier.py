"""
Document classification client + routing.

This mirrors the canonical document pipeline used by the MSME `complete-onboarding`
page: a file is POSTed to the classifier (`/api/v1/documents/classify`), the returned
label is mapped to a backend `DocumentType`, and the document is routed to the right
entity type / KYC stage before being uploaded through `/kyc/upload-document`.

Keeping the mapping here (instead of asking the agent/LLM to guess a document type)
is what makes WhatsApp uploads land in the correct slot — identical to a drag-and-drop
on the portal.
"""
from typing import Any, Dict, Optional, Tuple

from shared.config import settings

from .madad_client import MadadAPIClient, MadadAPIError

CLASSIFY_PATH = "/api/v1/documents/classify"

# Classifier label -> backend DocumentType enum. Superset of the MSME portal map
# (app/complete-onboarding/page.tsx CLASSIFICATION_LABEL_TO_DOC_TYPE).
CLASSIFICATION_LABEL_TO_DOC_TYPE: Dict[str, str] = {
    "Commercial Registration": "COMMERCIAL_REGISTRATION",
    "Trade License": "TRADE_LICENSE",
    "Tax Card": "TAX_CARD",
    "Establishment Card": "ESTABLISHMENT_CARD",
    "Article of Association": "ARTICLE_OF_ASSOCIATION",
    "Credit Bureau Report (Business)": "COMMERCIAL_CREDIT_REPORT",
    "Payable Ageing Report": "PAYABLE_AGING_REPORT",
    "Receivable Ageing Report": "RECEIVABLES_AGING_REPORT",
    "Bank Statement": "BANK_STATEMENT",
    "Audited Financial Report": "AUDITED_FINANCIAL_REPORT",
    "Interim Financial Report": "INTERIM_FINANCIAL_REPORT",
    "Passport": "SHAREHOLDER_PASSPORT",
    "QID (Qatar ID)": "SHAREHOLDER_QID",
    "National Address": "BUSINESS_ADDRESS_PROOF",
    "Credit Bureau Report (Individual)": "SHAREHOLDER_CREDIT_BUREAU_REPORT",
}

BUSINESS_DOC_TYPES = {
    "COMMERCIAL_REGISTRATION",
    "TRADE_LICENSE",
    "TAX_CARD",
    "ESTABLISHMENT_CARD",
    "BUSINESS_ADDRESS_PROOF",
    "ARTICLE_OF_ASSOCIATION",
}

FINANCIAL_DOC_TYPES = {
    "COMMERCIAL_CREDIT_REPORT",
    "RECEIVABLES_AGING_REPORT",
    "PAYABLE_AGING_REPORT",
    "BANK_STATEMENT",
    "INTERIM_FINANCIAL_REPORT",
    "AUDITED_FINANCIAL_REPORT",
}

SHAREHOLDER_DOC_TYPES = {
    "SHAREHOLDER_PASSPORT",
    "SHAREHOLDER_QID",
    "SHAREHOLDER_PROOF_OF_ADDRESS",
    "SHAREHOLDER_CREDIT_BUREAU_REPORT",
}

ADDITIONAL_DOCUMENT = "ADDITIONAL_DOCUMENT"


def map_classification_to_doc_type(label: Optional[str]) -> Optional[str]:
    """Map a classifier label to a backend DocumentType, or None if unmapped."""
    if not label:
        return None
    return CLASSIFICATION_LABEL_TO_DOC_TYPE.get(label.strip())


def route_document_type(doc_type: str) -> Tuple[str, str]:
    """
    Return (document_entity_type, kyc_stage) for a backend DocumentType — the same
    routing the portal uses (business vs financial vs shareholder vs additional).
    """
    if doc_type in BUSINESS_DOC_TYPES:
        return "BUSINESS_DETAILS", "Business Documents"
    if doc_type in FINANCIAL_DOC_TYPES:
        return "BUSINESS_DETAILS", "Financial Documents"
    if doc_type in SHAREHOLDER_DOC_TYPES:
        # The backend parks shareholder docs on the business and auto-assigns them
        # to the matching shareholder (by extracted ID) once extracted — so no
        # shareholder_id / document_param is required here.
        return "SHAREHOLDER", "Shareholder Documents"
    return "BUSINESS_DETAILS", "Additional Documents"


class DocumentClassifierClient:
    """Thin async client for the document-classifier `/classify` endpoint."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.raw_url = base_url or settings.DOCUMENT_CLASSIFIER_URL
        self.timeout = timeout or settings.DOCUMENT_CLASSIFIER_TIMEOUT

    def _split_url(self) -> Tuple[str, str]:
        if not self.raw_url:
            raise MadadAPIError(
                "DOCUMENT_CLASSIFIER_URL is required to classify documents"
            )
        url = self.raw_url.rstrip("/")
        if url.endswith(CLASSIFY_PATH):
            return url[: -len(CLASSIFY_PATH)], CLASSIFY_PATH
        return url, CLASSIFY_PATH

    async def classify_bytes(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """POST bytes to the classifier and return its parsed JSON body."""
        base_url, path = self._split_url()
        client = MadadAPIClient(base_url=base_url, timeout=self.timeout)
        response = await client.upload_file_bytes(
            path,
            file_name=file_name,
            file_bytes=file_bytes,
            content_type=mime_type,
            form_data={},
        )
        body = response.get("body")
        return body if isinstance(body, dict) else {}
