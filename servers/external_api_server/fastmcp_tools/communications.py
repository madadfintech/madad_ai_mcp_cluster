from typing import Any, Dict, List, Optional

from tools.api_wrappers.external.external_vendor import MadadCommunicationsAPI, WhatsAppCloudAPI

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
async def whatsapp_cloud_send_text(to: str, body: str, preview_url: bool = False) -> Dict[str, Any]:
    """Send a WhatsApp text message directly through Meta Cloud API."""
    return await WhatsAppCloudAPI().send_text(to=to, body=body, preview_url=preview_url)


@mcp.tool
async def whatsapp_cloud_send_template(
    to: str,
    template_name: str,
    language_code: str = "en_US",
    components: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Send a WhatsApp template message directly through Meta Cloud API."""
    return await WhatsAppCloudAPI().send_template(
        to=to,
        template_name=template_name,
        language_code=language_code,
        components=components,
    )
