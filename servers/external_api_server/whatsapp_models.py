from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WhatsAppTextRequest(BaseModel):
    to: str = Field(description="Recipient WhatsApp number in international format.")
    body: str = Field(description="Text message body.")
    preview_url: bool = False


class WhatsAppTemplateRequest(BaseModel):
    to: str = Field(description="Recipient WhatsApp number in international format.")
    template_name: str
    language_code: str = "en"
    components: Optional[List[Dict[str, Any]]] = None


class WhatsAppDocumentLinkRequest(BaseModel):
    to: str = Field(description="Recipient WhatsApp number in international format.")
    document_url: str
    filename: Optional[str] = None
    caption: Optional[str] = None


class WhatsAppMarkReadRequest(BaseModel):
    message_id: str
