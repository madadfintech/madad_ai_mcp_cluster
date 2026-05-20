from typing import Optional

from tools.api_wrappers.common import MadadAPIClient
from tools.api_wrappers.external.external_vendor import MadadAuthExternalVendorAPI
from tools.api_wrappers.read.non_transactional import MadadAuthReadAPI
from tools.api_wrappers.write.transactional import MadadAuthTransactionalWriteAPI


class MadadAuthAPI:
    """Convenience wrapper for Madad auth endpoints."""

    def __init__(self, client: Optional[MadadAPIClient] = None):
        client = client or MadadAPIClient()
        self.read = MadadAuthReadAPI(client)
        self.write = MadadAuthTransactionalWriteAPI(client)
        self.external = MadadAuthExternalVendorAPI(client)

        self.check_contact = self.read.check_contact
        self.me = self.read.me

        self.send_otp = self.write.send_otp
        self.verify_otp = self.write.verify_otp
        self.onboarding_send_email = self.write.onboarding_send_email
        self.verify_onboarding_email = self.write.verify_onboarding_email
        self.onboarding_send_phone = self.write.onboarding_send_phone
        self.onboarding_verify_phone = self.write.onboarding_verify_phone
        self.complete_onboarding = self.write.complete_onboarding
        self.complete_google_onboarding = self.write.complete_google_onboarding
        self.refresh = self.write.refresh
        self.logout = self.write.logout

        self.google_oauth_url = self.external.google_oauth_url
        self.google_callback = self.external.google_callback
