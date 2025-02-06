from django.urls import path
from accounts.views import (
    CreateSubUserView,
    DeactivateActivateSubAccountAPIView,
    LoginAPIView,
    NINVerificationAPIView,
    RegistrationAPIView,
    ResendOTPView,
    SubAccountDetailAPIView,
    SubAccountListAPIView,
    VerifyOTPAPIView,
)


urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("create/sub-account/", CreateSubUserView.as_view(), name="create_sub_account"),
    path("detail/sub-account/<slug:slug>/", SubAccountDetailAPIView.as_view(), name="detail_sub_account"),
    path("list/sub-account/", SubAccountListAPIView.as_view(), name="list_sub_account"),
    path("deactivate-activate/sub-account/<slug:slug>/", DeactivateActivateSubAccountAPIView.as_view(), name="deactivate_activate_sub_account"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify-nin/", NINVerificationAPIView.as_view(), name="verify_nin"),
]
