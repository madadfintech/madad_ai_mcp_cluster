from typing import Any, Dict, List, Optional

import httpx

from shared.config import settings


class WhatsAppAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class WhatsAppCloudAPI:
    def __init__(
        self,
        *,
        graph_api_base_url: Optional[str] = None,
        graph_api_version: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.graph_api_base_url = (graph_api_base_url or settings.WHATSAPP_GRAPH_API_BASE_URL).rstrip("/")
        self.graph_api_version = graph_api_version or settings.WHATSAPP_GRAPH_API_VERSION
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.timeout = timeout or settings.WHATSAPP_API_TIMEOUT

        missing = [
            name
            for name, value in {
                "WHATSAPP_GRAPH_API_VERSION": self.graph_api_version,
                "WHATSAPP_PHONE_NUMBER_ID": self.phone_number_id,
                "WHATSAPP_ACCESS_TOKEN": self.access_token,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(f"Missing WhatsApp config: {', '.join(missing)}")

    @property
    def messages_url(self) -> str:
        return f"{self.graph_api_base_url}/{self.graph_api_version}/{self.phone_number_id}/messages"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            body = response.text

        if response.status_code >= 400:
            raise WhatsAppAPIError(
                f"WhatsApp API returned HTTP {response.status_code}",
                status_code=response.status_code,
                details=body,
            )

        return {"status_code": response.status_code, "body": body}

    async def send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.messages_url, json=payload, headers=self._headers())
        return self._parse_response(response)

    async def send_text(
        self,
        *,
        to: str,
        body: str,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        return await self.send_message(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "preview_url": preview_url,
                    "body": body,
                },
            }
        )

    async def send_template(
        self,
        *,
        to: str,
        template_name: str,
        language_code: str,
        components: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        template: Dict[str, Any] = {
            "name": template_name,
            "language": {"code": language_code},
        }
        if components:
            template["components"] = components

        return await self.send_message(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "template",
                "template": template,
            }
        )

    async def send_document_link(
        self,
        *,
        to: str,
        document_url: str,
        filename: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        document: Dict[str, Any] = {"link": document_url}
        if filename:
            document["filename"] = filename
        if caption:
            document["caption"] = caption

        return await self.send_message(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "document",
                "document": document,
            }
        )

    async def mark_read(self, *, message_id: str) -> Dict[str, Any]:
        return await self.send_message(
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            }
        )
