from typing import Any, Dict, Optional

from tools.api_wrappers.common import MadadAPIClient


def compact_payload(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


class MadadAuthTransactionalWriteAPI:
    """Write-capable Madad auth endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        self.client = client or MadadAPIClient()

    async def send_otp(
        self,
        *,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/send-otp",
            json_body=compact_payload(mobile=mobile, email=email, role=role),
        )

    async def verify_otp(
        self,
        *,
        otp: str,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/verify-otp",
            json_body=compact_payload(mobile=mobile, email=email, otp=otp, role=role),
        )

    async def onboarding_send_email(self, *, email: str, onboarding_token: str) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/onboarding-send-email",
            json_body={"email": email},
            bearer_token=onboarding_token,
        )

    async def verify_onboarding_email(
        self,
        *,
        email: str,
        otp: str,
        onboarding_token: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/verify-onboarding-email",
            json_body={"email": email, "otp": otp},
            bearer_token=onboarding_token,
        )

    async def onboarding_send_phone(self, *, phone: str, access_token: str) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/onboarding-send-phone",
            json_body={"phone": phone},
            bearer_token=access_token,
        )

    async def onboarding_verify_phone(
        self,
        *,
        phone: str,
        otp: str,
        access_token: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/onboarding-verify-phone",
            json_body={"phone": phone, "otp": otp},
            bearer_token=access_token,
        )

    async def complete_onboarding(
        self,
        *,
        first_name: str,
        last_name: str,
        legal_entity_name: str,
        cr_number: str,
        is_qatar_based: bool,
        email: str,
        phone: str,
        role: str,
        onboarding_token: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/complete-onboarding",
            json_body=compact_payload(
                firstName=first_name,
                lastName=last_name,
                legalEntityName=legal_entity_name,
                crNumber=cr_number,
                isQatarBased=is_qatar_based,
                email=email,
                phone=phone,
                role=role,
            ),
            bearer_token=onboarding_token,
        )

    async def complete_google_onboarding(
        self,
        *,
        first_name: str,
        last_name: str,
        legal_entity_name: str,
        cr_number: str,
        is_qatar_based: bool,
        email: str,
        phone: str,
        role: str,
        access_token: str,
    ) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/complete-google-onboarding",
            json_body={
                "firstName": first_name,
                "lastName": last_name,
                "legalEntityName": legal_entity_name,
                "crNumber": cr_number,
                "isQatarBased": is_qatar_based,
                "email": email,
                "phone": phone,
                "role": role,
            },
            bearer_token=access_token,
        )

    async def refresh(self, *, refresh_token: Optional[str] = None) -> Dict[str, Any]:
        return await self.client.request(
            "POST",
            "/auth/refresh",
            bearer_token=refresh_token,
        )

    async def logout(self, *, access_token: str) -> Dict[str, Any]:
        return await self.client.request("POST", "/auth/logout", bearer_token=access_token)
