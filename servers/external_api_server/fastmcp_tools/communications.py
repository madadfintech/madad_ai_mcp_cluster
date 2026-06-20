from typing import Any, Dict, List, Optional

from tools.api_wrappers.external.external_vendor import MadadCommunicationsAPI

from . import mcp


communications_api = MadadCommunicationsAPI()


@mcp.tool
async def madad_external_send_sms_otp(mobile: str, role: Optional[str] = None) -> Dict[str, Any]:
    """Send an OTP through the backend SMS integration."""
    return await communications_api.send_sms_otp(mobile=mobile, role=role)


@mcp.tool
async def madad_external_send_email_otp(email: str, role: Optional[str] = None) -> Dict[str, Any]:
    """Send an OTP through the backend email integration."""
    return await communications_api.send_email_otp(email=email, role=role)


@mcp.tool
async def madad_external_verify_otp(
    otp: str,
    mobile: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """Verify an OTP sent through SMS or email."""
    return await communications_api.verify_otp(otp=otp, mobile=mobile, email=email, role=role)


@mcp.tool
async def madad_external_send_whatsapp_text(
    to: str,
    body: str,
    preview_url: bool = False,
) -> Dict[str, Any]:
    """Send a WhatsApp text message through the Madad backend."""
    return await communications_api.send_whatsapp_text(to=to, body=body, preview_url=preview_url)


@mcp.tool
async def madad_external_send_whatsapp_interactive(
    to: str,
    body: str,
    buttonText: str,
    buttonUrl: str,
    header: Optional[str] = None,
    footer: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a WhatsApp interactive Call-To-Action URL button (e.g. a
    'Pay QAR 6,000 →' button that opens a payment link) through the Madad
    backend, instead of a raw link in the message body. The button label
    (buttonText) is capped at 20 characters by Meta."""
    return await communications_api.send_whatsapp_interactive_cta(
        to=to,
        body=body,
        button_text=buttonText,
        button_url=buttonUrl,
        header=header,
        footer=footer,
    )


@mcp.tool
async def madad_external_send_whatsapp_template(
    to: str,
    template_name: str,
    language_code: str = "en_US",
    components: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Send a WhatsApp template message through the Madad backend."""
    return await communications_api.send_whatsapp_template(
        to=to,
        template_name=template_name,
        language_code=language_code,
        components=components,
    )


@mcp.tool
async def madad_external_send_whatsapp_document(
    to: str,
    filename: str,
    content_base64: str,
    mime_type: Optional[str] = None,
    caption: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a WhatsApp DOCUMENT (file attachment) through the Madad backend.

    The backend uploads the bytes to Meta's media endpoint and then sends a
    document message referencing the resulting media id. Used for the
    bulk-invoice review CSV the SME edits and sends back. ``content_base64`` is
    the raw file bytes (base64, no ``data:`` prefix); ``caption`` shows under
    the file and ``filename`` is the name the recipient downloads."""
    return await communications_api.send_whatsapp_document(
        to=to,
        filename=filename,
        content_base64=content_base64,
        mime_type=mime_type,
        caption=caption,
    )


@mcp.tool
async def madad_external_send_email_text(
    to: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an arbitrary-content email (subject + body) through the Madad
    backend SendGrid path. Use this for the email onboarding thread — unlike
    madad_external_send_email_otp (which only sends a verification code and
    discards the body), this delivers full message content."""
    return await communications_api.send_email_text(
        to=to,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        reply_to=reply_to,
    )
