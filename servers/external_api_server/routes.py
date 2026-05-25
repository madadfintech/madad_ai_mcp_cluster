from fastapi import APIRouter, HTTPException
import random
from .models import *
from .madad_auth_models import (
    AccessTokenRequest,
    CheckContactRequest,
    CompleteGoogleOnboardingRequest,
    CompleteOnboardingRequest,
    OnboardingSendEmailRequest,
    OnboardingSendPhoneRequest,
    OnboardingVerifyPhoneRequest,
    RefreshTokenRequest,
    SendOtpRequest,
    VerifyOnboardingEmailRequest,
    VerifyOtpRequest,
)
from .madad_kyc_models import (
    UpdateEligibilityRequest,
    UploadAuditedFinancialReportRequest,
    UploadCommercialRegistrationRequest,
    UploadKYCDocumentRequest,
)
from .madad_communications_models import (
    SendBackendWhatsAppTemplateRequest,
    SendBackendWhatsAppTextRequest,
    SendEmailOtpRequest,
    SendSmsOtpRequest,
    VerifyCommunicationOtpRequest,
)
from .whatsapp_models import (
    WhatsAppDocumentLinkRequest,
    WhatsAppMarkReadRequest,
    WhatsAppTemplateRequest,
    WhatsAppTextRequest,
)
from datetime import datetime
from shared.logging_config import get_logger
from tools.api_wrappers.auth import MadadAuthAPI
from tools.api_wrappers.madad_client import MadadAPIError
from tools.api_wrappers.external.external_vendor import (
    MadadCommunicationsAPI,
    WhatsAppAPIError,
    WhatsAppCloudAPI,
)
from tools.api_wrappers.write.transactional import MadadKYCTransactionalWriteAPI

router = APIRouter()
logger = get_logger(__name__)
madad_auth_api = MadadAuthAPI()
madad_kyc_api = MadadKYCTransactionalWriteAPI()
madad_communications_api = MadadCommunicationsAPI()


def get_whatsapp_api() -> WhatsAppCloudAPI:
    return WhatsAppCloudAPI()


def madad_api_error_to_http(exc: MadadAPIError) -> HTTPException:
    status_code = exc.status_code if exc.status_code and exc.status_code >= 400 else 502
    return HTTPException(
        status_code=status_code,
        detail={
            "message": str(exc),
            "madad_status_code": exc.status_code,
            "madad_response": exc.details,
        },
    )


def whatsapp_api_error_to_http(exc: WhatsAppAPIError) -> HTTPException:
    status_code = exc.status_code if exc.status_code and exc.status_code >= 400 else 502
    return HTTPException(
        status_code=status_code,
        detail={
            "message": str(exc),
            "whatsapp_status_code": exc.status_code,
            "whatsapp_response": exc.details,
        },
    )


def whatsapp_config_error_to_http(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=400, detail={"message": str(exc)})

# Static responses for dummy APIs
DUMMY_NEWS = """
Breaking: Major advancements in AI technology announced today. Leading tech 
companies showcase new language models with unprecedented capabilities. Industry 
experts predict significant impact on enterprise automation and productivity tools.
"""

DUMMY_WEATHER_ADVICE = """
Weather Advisory: Based on current conditions, we recommend:
- Morning: Light jacket recommended, temperatures rising
- Afternoon: Peak sunshine hours, stay hydrated
- Evening: Cooling down, perfect for outdoor activities
- Air quality: Good, suitable for all activities
"""

@router.post("/search/serp", response_model=SerpSearchResponse)
async def run_serp_search(request: SerpSearchRequest):
    """Perform a SERP search - DUMMY API with static results"""
    logger.info("SERP search request", query=request.query, num_results=request.num_results)
    
    # Mock SERP results
    mock_results = [
        SerpResult(
            title=f"Result {i}: {request.query} - Comprehensive Guide",
            url=f"https://example{i}.com/{request.query.replace(' ', '-')}",
            snippet=f"Discover everything about {request.query}. Expert insights, tutorials, and best practices for {request.query}.",
            rank=i
        )
        for i in range(1, min(request.num_results + 1, 11))
    ]
    
    logger.info("SERP search completed", results_count=len(mock_results))
    
    return SerpSearchResponse(
        query=request.query,
        results=mock_results,
        total_results=len(mock_results)
    )

@router.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest):
    """Get weather information - DUMMY API with random data"""
    logger.info("Weather request", location=request.location, units=request.units)
    
    conditions = ["sunny", "partly cloudy", "cloudy", "light rain", "clear"]
    
    response = WeatherResponse(
        location=request.location,
        temperature=round(random.uniform(15, 30), 1),
        condition=random.choice(conditions),
        humidity=random.randint(40, 80),
        timestamp=datetime.now().isoformat()
    )
    
    logger.info("Weather response generated", location=request.location, condition=response.condition)
    return response

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text - DUMMY API with predefined translations"""
    logger.info("Translation request", 
               source=request.source_lang, 
               target=request.target_lang,
               text_length=len(request.text))
    
    translations = {
        ("en", "es"): "Texto traducido al español",
        ("en", "fr"): "Texte traduit en français",
        ("en", "de"): "Ins Deutsche übersetzter Text",
        ("es", "en"): "Text translated to English",
        ("fr", "en"): "Text translated to English",
        ("de", "en"): "Text translated to English",
    }
    
    key = (request.source_lang, request.target_lang)
    translated = translations.get(key, f"[TRANSLATED from {request.source_lang} to {request.target_lang}]: {request.text}")
    
    logger.info("Translation completed")
    
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated,
        source_language=request.source_lang,
        target_language=request.target_lang,
        confidence=random.uniform(0.85, 0.99)
    )

@router.get("/external/status")
async def get_external_api_status():
    """Get status of external API connections - DUMMY API"""
    return {
        "serp_api": "operational",
        "weather_api": "operational", 
        "translation_api": "operational",
        "last_check": datetime.now().isoformat(),
        "response_times_ms": {
            "serp": 125,
            "weather": 85,
            "translation": 95
        }
    }

@router.get("/dummy/news")
async def get_latest_news():
    """Get latest news - DUMMY API with static content"""
    return {
        "headline": "AI Technology Breakthrough",
        "content": DUMMY_NEWS.strip(),
        "category": "Technology",
        "published": datetime.now().isoformat(),
        "source": "TechNews Global"
    }

@router.get("/dummy/advice")
async def get_weather_advice():
    """Get weather advice - DUMMY API with static content"""
    return {
        "title": "Daily Weather Advisory",
        "advice": DUMMY_WEATHER_ADVICE.strip(),
        "generated": datetime.now().isoformat(),
        "valid_until": "End of day"
    }


@router.post("/madad/auth/send-otp")
async def madad_auth_send_otp(request: SendOtpRequest):
    """Send OTP to a mobile number or email address."""
    try:
        return await madad_auth_api.send_otp(
            mobile=request.mobile,
            email=request.email,
            role=request.role,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/verify-otp")
async def madad_auth_verify_otp(request: VerifyOtpRequest):
    """Verify OTP and authenticate a user."""
    try:
        return await madad_auth_api.verify_otp(
            mobile=request.mobile,
            email=request.email,
            otp=request.otp,
            role=request.role,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/check-contact")
async def madad_auth_check_contact(request: CheckContactRequest):
    """Check whether a mobile number or email is registered."""
    try:
        return await madad_auth_api.check_contact(mobile=request.mobile, email=request.email)
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/onboarding-send-email")
async def madad_auth_onboarding_send_email(request: OnboardingSendEmailRequest):
    """Send onboarding email OTP using an onboarding token."""
    try:
        return await madad_auth_api.onboarding_send_email(
            email=request.email,
            onboarding_token=request.onboarding_token,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/verify-onboarding-email")
async def madad_auth_verify_onboarding_email(request: VerifyOnboardingEmailRequest):
    """Verify onboarding email OTP using an onboarding token."""
    try:
        return await madad_auth_api.verify_onboarding_email(
            email=request.email,
            otp=request.otp,
            onboarding_token=request.onboarding_token,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/onboarding-send-phone")
async def madad_auth_onboarding_send_phone(request: OnboardingSendPhoneRequest):
    """Send onboarding phone OTP using an access token."""
    try:
        return await madad_auth_api.onboarding_send_phone(
            phone_number=request.phone_number,
            access_token=request.access_token,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/onboarding-verify-phone")
async def madad_auth_onboarding_verify_phone(request: OnboardingVerifyPhoneRequest):
    """Verify onboarding phone OTP using an access token."""
    try:
        return await madad_auth_api.onboarding_verify_phone(
            phone_number=request.phone_number,
            otp=request.otp,
            access_token=request.access_token,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/complete-onboarding")
async def madad_auth_complete_onboarding(request: CompleteOnboardingRequest):
    """Complete onboarding and create the user account."""
    try:
        return await madad_auth_api.complete_onboarding(
            first_name=request.first_name,
            last_name=request.last_name,
            onboarding_token=request.onboarding_token,
            email=request.email,
            phone_number=request.phone_number,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/complete-google-onboarding")
async def madad_auth_complete_google_onboarding(request: CompleteGoogleOnboardingRequest):
    """Complete onboarding after Google OAuth login."""
    try:
        return await madad_auth_api.complete_google_onboarding(
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
            access_token=request.access_token,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.get("/madad/auth/google")
async def madad_auth_google():
    """Initiate Google OAuth and return redirect metadata."""
    try:
        return await madad_auth_api.google_oauth_url()
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.get("/madad/auth/google/callback")
async def madad_auth_google_callback():
    """Call the Google OAuth callback endpoint."""
    try:
        return await madad_auth_api.google_callback()
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/refresh")
async def madad_auth_refresh(request: RefreshTokenRequest):
    """Refresh access token with refresh token or API cookies."""
    try:
        return await madad_auth_api.refresh(refresh_token=request.refresh_token)
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.get("/madad/auth/me")
async def madad_auth_me(access_token: str):
    """Get the profile for the current access token."""
    try:
        return await madad_auth_api.me(access_token=access_token)
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/auth/logout")
async def madad_auth_logout(request: AccessTokenRequest):
    """Log out the current access token."""
    try:
        return await madad_auth_api.logout(access_token=request.access_token)
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/external/sms/send-otp")
async def madad_external_sms_send_otp(request: SendSmsOtpRequest):
    """Send an OTP via the backend SMS provider."""
    try:
        return await madad_communications_api.send_sms_otp(
            mobile=request.mobile,
            role=request.role,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/external/email/send-otp")
async def madad_external_email_send_otp(request: SendEmailOtpRequest):
    """Send an OTP via the backend email provider."""
    try:
        return await madad_communications_api.send_email_otp(
            email=request.email,
            role=request.role,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/external/otp/verify")
async def madad_external_otp_verify(request: VerifyCommunicationOtpRequest):
    """Verify an OTP sent by SMS or email."""
    try:
        return await madad_communications_api.verify_otp(
            otp=request.otp,
            mobile=request.mobile,
            email=request.email,
            role=request.role,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/external/whatsapp/send-text")
async def madad_external_whatsapp_send_text(request: SendBackendWhatsAppTextRequest):
    """Send a WhatsApp text message through the Madad backend."""
    try:
        return await madad_communications_api.send_whatsapp_text(
            to=request.to,
            body=request.body,
            preview_url=request.preview_url,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/external/whatsapp/send-template")
async def madad_external_whatsapp_send_template(request: SendBackendWhatsAppTemplateRequest):
    """Send a WhatsApp template message through the Madad backend."""
    try:
        return await madad_communications_api.send_whatsapp_template(
            to=request.to,
            template_name=request.template_name,
            language_code=request.language_code,
            components=request.components,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.patch("/madad/kyc/eligibility")
async def madad_kyc_update_eligibility(request: UpdateEligibilityRequest):
    """Update business eligibility details."""
    try:
        return await madad_kyc_api.update_eligibility(
            access_token=request.access_token,
            is_qatar_based=request.is_qatar_based,
            business_age=request.business_age,
            cr_validity=request.cr_validity,
            company_type=request.company_type,
            sector=request.sector,
            turnover=request.turnover,
            employees=request.employees,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/kyc/upload-document")
async def madad_kyc_upload_document(request: UploadKYCDocumentRequest):
    """Upload a KYC document."""
    try:
        return await madad_kyc_api.upload_document(
            file_path=request.file_path,
            document_entity_type=request.document_entity_type,
            document_type=request.document_type,
            access_token=request.access_token,
            kyc_stage=request.kyc_stage,
            document_param=request.document_param,
            from_admin=request.from_admin,
            target_user_id=request.target_user_id,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/kyc/upload-commercial-registration")
async def madad_kyc_upload_commercial_registration(request: UploadCommercialRegistrationRequest):
    """Upload a commercial registration document."""
    try:
        return await madad_kyc_api.upload_commercial_registration(
            file_path=request.file_path,
            access_token=request.access_token,
            document_entity_type=request.document_entity_type,
            document_type=request.document_type,
            kyc_stage=request.kyc_stage,
            document_param=request.document_param,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/madad/kyc/upload-audited-financial-report")
async def madad_kyc_upload_audited_financial_report(request: UploadAuditedFinancialReportRequest):
    """Upload an audited financial report."""
    try:
        return await madad_kyc_api.upload_audited_financial_report(
            file_path=request.file_path,
            access_token=request.access_token,
            document_entity_type=request.document_entity_type,
            document_type=request.document_type,
            kyc_stage=request.kyc_stage,
            document_param=request.document_param,
        )
    except MadadAPIError as exc:
        raise madad_api_error_to_http(exc)


@router.post("/whatsapp/send-text")
async def whatsapp_send_text(request: WhatsAppTextRequest):
    """Send a WhatsApp text message."""
    try:
        return await get_whatsapp_api().send_text(
            to=request.to,
            body=request.body,
            preview_url=request.preview_url,
        )
    except WhatsAppAPIError as exc:
        raise whatsapp_api_error_to_http(exc)
    except ValueError as exc:
        raise whatsapp_config_error_to_http(exc)


@router.post("/whatsapp/send-template")
async def whatsapp_send_template(request: WhatsAppTemplateRequest):
    """Send a WhatsApp template message."""
    try:
        return await get_whatsapp_api().send_template(
            to=request.to,
            template_name=request.template_name,
            language_code=request.language_code,
            components=request.components,
        )
    except WhatsAppAPIError as exc:
        raise whatsapp_api_error_to_http(exc)
    except ValueError as exc:
        raise whatsapp_config_error_to_http(exc)


@router.post("/whatsapp/send-document-link")
async def whatsapp_send_document_link(request: WhatsAppDocumentLinkRequest):
    """Send a WhatsApp document message by URL."""
    try:
        return await get_whatsapp_api().send_document_link(
            to=request.to,
            document_url=request.document_url,
            filename=request.filename,
            caption=request.caption,
        )
    except WhatsAppAPIError as exc:
        raise whatsapp_api_error_to_http(exc)
    except ValueError as exc:
        raise whatsapp_config_error_to_http(exc)


@router.post("/whatsapp/mark-read")
async def whatsapp_mark_read(request: WhatsAppMarkReadRequest):
    """Mark a WhatsApp message as read."""
    try:
        return await get_whatsapp_api().mark_read(message_id=request.message_id)
    except WhatsAppAPIError as exc:
        raise whatsapp_api_error_to_http(exc)
    except ValueError as exc:
        raise whatsapp_config_error_to_http(exc)
