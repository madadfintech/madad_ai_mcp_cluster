from typing import Any, Dict, Optional

from tools.api_wrappers.auth import MadadAuthAPI

from . import mcp


auth_api = MadadAuthAPI()


@mcp.tool
async def madad_auth_send_otp(
    mobile: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a Madad login OTP to a mobile number or email address."""
    return await auth_api.send_otp(mobile=mobile, email=email, role=role)


@mcp.tool
async def madad_auth_verify_otp(
    otp: str,
    mobile: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """Verify a Madad OTP and return the authenticated session response."""
    return await auth_api.verify_otp(mobile=mobile, email=email, otp=otp, role=role)


@mcp.tool
async def madad_auth_check_contact(
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """Check whether a mobile number or email is already registered in Madad."""
    return await auth_api.check_contact(phone=phone, email=email)


@mcp.tool
async def madad_auth_me(access_token: str) -> Dict[str, Any]:
    """Get the current Madad user profile, journey status, and business details."""
    return await auth_api.me(access_token=access_token)


@mcp.tool
async def madad_auth_onboarding_send_email(email: str, onboarding_token: str) -> Dict[str, Any]:
    """Send an email OTP during onboarding using an onboarding token."""
    return await auth_api.onboarding_send_email(email=email, onboarding_token=onboarding_token)


@mcp.tool
async def madad_auth_verify_onboarding_email(
    email: str,
    otp: str,
    onboarding_token: str,
) -> Dict[str, Any]:
    """Verify an onboarding email OTP using an onboarding token."""
    return await auth_api.verify_onboarding_email(
        email=email,
        otp=otp,
        onboarding_token=onboarding_token,
    )


@mcp.tool
async def madad_auth_onboarding_send_phone(phone: str, access_token: str) -> Dict[str, Any]:
    """Send a phone OTP during onboarding using an access token."""
    return await auth_api.onboarding_send_phone(phone=phone, access_token=access_token)


@mcp.tool
async def madad_auth_onboarding_verify_phone(
    phone: str,
    otp: str,
    access_token: str,
) -> Dict[str, Any]:
    """Verify an onboarding phone OTP using an access token."""
    return await auth_api.onboarding_verify_phone(
        phone=phone,
        otp=otp,
        access_token=access_token,
    )


@mcp.tool
async def madad_auth_complete_onboarding(
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
    """Complete standard onboarding and create the Madad user account."""
    return await auth_api.complete_onboarding(
        first_name=first_name,
        last_name=last_name,
        legal_entity_name=legal_entity_name,
        cr_number=cr_number,
        is_qatar_based=is_qatar_based,
        email=email,
        phone=phone,
        role=role,
        onboarding_token=onboarding_token,
    )


@mcp.tool
async def madad_auth_complete_google_onboarding(
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
    """Complete onboarding after a Google OAuth login."""
    return await auth_api.complete_google_onboarding(
        first_name=first_name,
        last_name=last_name,
        legal_entity_name=legal_entity_name,
        cr_number=cr_number,
        is_qatar_based=is_qatar_based,
        email=email,
        phone=phone,
        role=role,
        access_token=access_token,
    )


@mcp.tool
async def madad_auth_refresh(refresh_token: Optional[str] = None) -> Dict[str, Any]:
    """Refresh a Madad access token with a refresh token when available."""
    return await auth_api.refresh(refresh_token=refresh_token)


@mcp.tool
async def madad_auth_logout(access_token: str) -> Dict[str, Any]:
    """Log out the current Madad access token."""
    return await auth_api.logout(access_token=access_token)


@mcp.tool
async def madad_auth_google_oauth_url() -> Dict[str, Any]:
    """Start the Madad Google OAuth login flow and return redirect metadata."""
    return await auth_api.google_oauth_url()
