from typing import Any, Dict, List, Optional

from tools.api_wrappers.madad_client import MadadAPIClient


class MadadCommunicationsAPI:
    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def send_sms_otp(self, mobile: str, role: Optional[str] = None) -> Dict[str, Any]:
        payload = {"mobile": mobile}
        if role:
            payload["role"] = role
        return await self.client.request("POST", "/auth/send-otp", json_body=payload)

    async def send_email_otp(self, email: str, role: Optional[str] = None) -> Dict[str, Any]:
        payload = {"email": email}
        if role:
            payload["role"] = role
        return await self.client.request("POST", "/auth/send-otp", json_body=payload)

    async def verify_otp(
        self,
        otp: str,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"otp": otp}
        if mobile:
            payload["mobile"] = mobile
        if email:
            payload["email"] = email
        if role:
            payload["role"] = role
        return await self.client.request("POST", "/auth/verify-otp", json_body=payload)

    async def send_whatsapp_text(
        self,
        to: str,
        body: str,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/whatsapp/messages/text",
            json_body={
                "to": to,
                "body": body,
                "previewUrl": preview_url,
            },
        )

    async def send_whatsapp_interactive_cta(
        self,
        to: str,
        body: str,
        button_text: str,
        button_url: str,
        header: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "to": to,
            "body": body,
            "buttonText": button_text,
            "buttonUrl": button_url,
        }
        if header:
            payload["header"] = header
        if footer:
            payload["footer"] = footer

        return await self.client.request(
            "POST",
            "/whatsapp/messages/interactive-cta",
            json_body=payload,
        )

    async def send_whatsapp_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "to": to,
            "templateName": template_name,
            "languageCode": language_code,
        }
        if components:
            payload["components"] = components

        return await self.client.request(
            "POST",
            "/whatsapp/messages/template",
            json_body=payload,
        )

    async def send_email_text(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "to": to,
            "subject": subject,
            "bodyText": body_text,
        }
        if body_html:
            payload["bodyHtml"] = body_html
        if reply_to:
            payload["replyTo"] = reply_to

        return await self.client.request(
            "POST",
            "/email/send-text",
            json_body=payload,
        )
