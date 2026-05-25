from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SendSmsOtpRequest(BaseModel):
    mobile: str = Field(description="Recipient mobile number.")
    role: Optional[str] = None


class SendEmailOtpRequest(BaseModel):
    email: str = Field(description="Recipient email address.")
    role: Optional[str] = None


class VerifyCommunicationOtpRequest(BaseModel):
    otp: str = Field(description="OTP code to verify.")
    mobile: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class SendBackendWhatsAppTextRequest(BaseModel):
    to: str = Field(description="Recipient WhatsApp number in international format.")
    body: str = Field(description="Text message body.")
    preview_url: bool = False


class SendBackendWhatsAppTemplateRequest(BaseModel):
    to: str = Field(description="Recipient WhatsApp number in international format.")
    template_name: str
    language_code: str = "en_US"
    components: Optional[List[Dict[str, Any]]] = None
