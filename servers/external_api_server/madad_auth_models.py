from typing import Optional

from pydantic import BaseModel, Field

try:
    from pydantic import model_validator

    HAS_MODEL_VALIDATOR = True
except ImportError:
    from pydantic import root_validator

    HAS_MODEL_VALIDATOR = False


class ContactIdentifierMixin(BaseModel):
    mobile: Optional[str] = Field(default=None, description="Qatar mobile number.")
    email: Optional[str] = Field(default=None, description="Email address.")

    if HAS_MODEL_VALIDATOR:

        @model_validator(mode="after")
        def require_mobile_or_email(self):
            if not self.mobile and not self.email:
                raise ValueError("Either mobile or email is required.")
            return self

    else:

        @root_validator
        def require_mobile_or_email(cls, values):
            if not values.get("mobile") and not values.get("email"):
                raise ValueError("Either mobile or email is required.")
            return values


class SendOtpRequest(ContactIdentifierMixin):
    role: Optional[str] = Field(default=None, description="Optional role hint such as ADMIN.")


class VerifyOtpRequest(ContactIdentifierMixin):
    otp: str = Field(description="6-digit OTP code.")
    role: Optional[str] = Field(default=None, description="Optional role hint such as ADMIN.")


class CheckContactRequest(ContactIdentifierMixin):
    pass


class OnboardingSendEmailRequest(BaseModel):
    email: str
    onboarding_token: str = Field(description="Bearer onboarding token.")


class VerifyOnboardingEmailRequest(BaseModel):
    email: str
    otp: str
    onboarding_token: str = Field(description="Bearer onboarding token.")


class OnboardingSendPhoneRequest(BaseModel):
    phone_number: str = Field(description="Mobile number to send OTP to.")
    access_token: str = Field(description="Bearer access token.")


class OnboardingVerifyPhoneRequest(BaseModel):
    phone_number: str = Field(description="Mobile number that received the OTP.")
    otp: str
    access_token: str = Field(description="Bearer access token.")


class CompleteOnboardingRequest(BaseModel):
    first_name: str
    last_name: str
    onboarding_token: str = Field(description="Bearer onboarding token.")
    email: Optional[str] = None
    phone_number: Optional[str] = None


class CompleteGoogleOnboardingRequest(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    access_token: str = Field(description="Bearer access token.")


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = Field(
        default=None,
        description="Optional bearer refresh token. If omitted, the API may rely on cookies.",
    )


class AccessTokenRequest(BaseModel):
    access_token: str = Field(description="Bearer access token.")
